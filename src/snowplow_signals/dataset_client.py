from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel

from .api_client import ApiClient
from .models import (
    Anchors,
    AttributeGroup,
    DatasetAttributeGroups,
    DatasetBundle,
    WarehouseTable,
)
from .models.dataset import Manifest, ManifestDefinition, ManifestTables
from .models.execution import ExecutionError, ExecutionResult
from .models.model import (
    AttributeGroupResponse,
    AttributeSqlFile,
    DatasetBundleRequest,
    DatasetBundleResponse,
    DatasetSqlFile,
    SessionAnchors,
    UserSuppliedAnchors,
)

if TYPE_CHECKING:
    from .models.connection import WarehouseConnection


class DatasetClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def build_sql(
        self,
        attribute_groups: list[AttributeGroup | AttributeGroupResponse],
        anchors: Anchors,
        attributes_database: str | None = None,
        attributes_schema: str | None = None,
        attributes_table_prefix: str | None = None,
        dataset: WarehouseTable | None = None,
        max_lookback_days: int | None = None,
    ) -> DatasetBundle:
        resolved_groups = [
            (
                ag
                if isinstance(ag, AttributeGroup)
                else AttributeGroup.model_validate(ag.model_dump())
            )
            for ag in attribute_groups
        ]
        request = DatasetBundleRequest(
            anchors=anchors,
            attributes=DatasetAttributeGroups(
                attribute_groups=resolved_groups,
                database=attributes_database,
                schema=attributes_schema,
                table_prefix=attributes_table_prefix,
            ),
            dataset=dataset,
            max_lookback_days=max_lookback_days,
        )

        data = self._model_dump(request)
        raw_response = self.api_client.make_request("POST", "datasets/sql", data=data)
        response = DatasetBundleResponse.model_validate(raw_response)

        return DatasetBundle(
            request=request,
            response=response,
            dataset_client=self,
        )

    def save_dataset_bundle(self, bundle: DatasetBundle, path: str | Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        for filename, content in bundle.files.items():
            (path / filename).write_text(content)

        manifest = self._build_manifest(bundle)
        (path / "manifest.json").write_text(
            manifest.model_dump_json(indent=2, by_alias=True, exclude_none=True) + "\n"
        )
        (path / "README.md").write_text(self._build_readme(bundle))

    def execute_dataset_bundle(
        self, bundle: DatasetBundle, connection: WarehouseConnection
    ) -> ExecutionResult:
        stages_to_run: list[
            tuple[
                Literal["anchors", "attributes", "dataset"],
                DatasetSqlFile | AttributeSqlFile,
            ]
        ] = []

        # Fixed order: anchors -> attributes -> dataset
        stages_to_run.append(("anchors", bundle.response.anchors))
        for attr_entry in bundle.response.attributes:
            stages_to_run.append(("attributes", attr_entry))
        stages_to_run.append(("dataset", bundle.response.dataset))

        for stage_name, entry in stages_to_run:
            if entry.sql is None:
                continue
            try:
                connection.execute(entry.sql)
            except Exception as e:
                raise ExecutionError(
                    failed_stage=stage_name,
                    failed_table=WarehouseTable(
                        database=entry.database,
                        schema=entry.schema_,
                        table=entry.table,
                    ),
                    cause=e,
                ) from e

        dataset = bundle.response.dataset
        return ExecutionResult(
            table=WarehouseTable(
                database=dataset.database,
                schema=dataset.schema_,
                table=dataset.table,
            ),
            connection=connection,
        )

    def _build_manifest(self, bundle: DatasetBundle) -> Manifest:
        return Manifest(
            generated_at=datetime.now(timezone.utc).isoformat(),
            definition=ManifestDefinition(
                anchors=bundle.request.anchors,
                attribute_groups=list(bundle.request.attributes.attribute_groups),
            ),
            tables=ManifestTables(
                anchors=DatasetSqlFile(
                    database=bundle.response.anchors.database,
                    schema=bundle.response.anchors.schema_,
                    table=bundle.response.anchors.table,
                    sql=None,
                ),
                attributes=[
                    AttributeSqlFile(
                        database=attr.database,
                        schema=attr.schema_,
                        table=attr.table,
                        sql=None,
                        attribute_key=attr.attribute_key,
                    )
                    for attr in bundle.response.attributes
                ],
                dataset=DatasetSqlFile(
                    database=bundle.response.dataset.database,
                    schema=bundle.response.dataset.schema_,
                    table=bundle.response.dataset.table,
                    sql=None,
                ),
            ),
            files=list(bundle.files.keys()),
        )

    def _build_readme(self, bundle: DatasetBundle) -> str:
        req = bundle.request
        resp = bundle.response

        # Build file list in execution order with descriptions
        file_entries: list[tuple[str, str]] = []
        anchors_file = resp.anchors.table + ".sql"
        file_entries.append(
            (
                anchors_file,
                "Builds the anchors table (one row per training example, with its label).",
            )
        )
        for attr in resp.attributes:
            attr_file = attr.table + ".sql"
            key_name = attr.attribute_key.name if attr.attribute_key else attr.table
            file_entries.append(
                (
                    attr_file,
                    f"Computes attributes keyed on {key_name}, joined to the anchors point-in-time.",
                )
            )
        dataset_file = resp.dataset.table + ".sql"
        file_entries.append(
            (
                dataset_file,
                "Assembles the final training dataset (anchors + all attributes).",
            )
        )

        # Anchoring description
        anchoring_desc = self._describe_anchoring(req)

        # Attribute group names
        attr_names = [ag.name for ag in req.attributes.attribute_groups]

        # Output tables in execution order
        output_tables = [resp.anchors.table]
        for attr in resp.attributes:
            output_tables.append(attr.table)
        output_tables.append(resp.dataset.table)

        lines = [
            "# Signals training-dataset SQL bundle",
            "",
            "This folder contains the SQL to build a training dataset from your Snowplow events,",
            "generated by the Snowplow Signals dataset builder. Each file creates one table;",
            "run them in the order below (each stage reads the previous stage's tables).",
            "",
            "## How to run",
            "",
            "Run the `.sql` files against your warehouse in the order listed below — e.g. paste",
            "each into a worksheet, or run them with your warehouse CLI / a scheduler. Each stage",
            "reads the tables the previous one created, so the order matters.",
            "",
            "Each file uses `CREATE OR REPLACE TABLE`, so re-running is safe and idempotent.",
            "",
            "## Files (run in this order)",
            "",
        ]
        for i, (filename, description) in enumerate(file_entries, 1):
            lines.append(f"{i}. `{filename}` — {description}")

        lines += [
            "",
            "## What this predicts",
            "",
            f"- **Anchoring:** {anchoring_desc}",
            f"- **Features from:** {', '.join(f'{name}' for name in attr_names)}.",
            "",
            "## Output tables",
            "",
        ]
        for table in output_tables:
            lines.append(f"- `{table}`")

        lines += [
            "",
            "Full configuration (anchors, goal, attribute groups) is in `manifest.json`.",
            "",
        ]
        return "\n".join(lines)

    @staticmethod
    def _describe_anchoring(req: DatasetBundleRequest) -> str:
        anchors = req.anchors
        if isinstance(anchors, SessionAnchors):
            span = anchors.training_span
            if span.start_time and span.end_time:
                start = span.start_time.strftime("%Y-%m-%d")
                end = span.end_time.strftime("%Y-%m-%d")
                return f"one training example per session, over the training span {start} \u2192 {end}."
            return "one training example per session."
        if isinstance(anchors, UserSuppliedAnchors):
            return "user-supplied custom anchors."
        return "custom anchoring strategy."

    def _model_dump(self, model: BaseModel) -> dict:
        return model.model_dump(
            mode="json",
            exclude_none=True,
            by_alias=True,
        )
