from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel

from .execution import ExecutionError, ExecutionResult
from .model import AttributeGroupReference, AttributeSqlFile, DatasetSqlFile

if TYPE_CHECKING:
    from .connection import WarehouseConnection
    from .dataset import DatasetBundle
    from .model import DatasetBundleRequest


class ManifestInput(BaseModel):
    anchors: dict[str, object]
    attribute_groups: list[AttributeGroupReference]


class ManifestOutput(BaseModel):
    anchors: DatasetSqlFile
    attributes: list[AttributeSqlFile]
    dataset: DatasetSqlFile


class Manifest(BaseModel):
    generated_at: str
    input: ManifestInput
    output: ManifestOutput
    files: list[str]


def save_bundle(bundle: DatasetBundle, path: str | Path) -> None:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    for filename, content in bundle.files.items():
        (path / filename).write_text(content)

    manifest = _build_manifest(bundle)
    (path / "manifest.json").write_text(
        manifest.model_dump_json(indent=2, by_alias=True) + "\n"
    )
    (path / "README.md").write_text(_build_readme(bundle))


def execute_bundle(
    bundle: DatasetBundle, connection: WarehouseConnection
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
            from .dataset import WarehouseTable

            raise ExecutionError(
                failed_stage=stage_name,
                failed_table=WarehouseTable(
                    database=entry.database,
                    schema=entry.schema_,
                    table=entry.table,
                ),
                cause=e,
            ) from e

    # SELECT back the final training table
    dataset = bundle.response.dataset
    parts = [
        v for v in [dataset.database, dataset.schema_, dataset.table] if v is not None
    ]
    fqn = ".".join(parts)
    try:
        dataframe = connection.fetch_pandas(f"SELECT * FROM {fqn}")
    except Exception as e:
        from .dataset import WarehouseTable

        raise ExecutionError(
            failed_stage="dataset",
            failed_table=WarehouseTable(
                database=dataset.database,
                schema=dataset.schema_,
                table=dataset.table,
            ),
            cause=e,
        ) from e

    return ExecutionResult(dataframe=dataframe)


def _build_manifest(bundle: DatasetBundle) -> Manifest:
    return Manifest(
        generated_at=datetime.now(timezone.utc).isoformat(),
        input=ManifestInput(
            anchors=bundle.request.anchors.model_dump(
                mode="json", exclude_none=True, by_alias=True
            ),
            attribute_groups=[
                AttributeGroupReference(name=ag.name, version=ag.version or 1)
                for ag in bundle.request.attributes.attribute_groups
            ],
        ),
        output=ManifestOutput(
            anchors=bundle.response.anchors,
            attributes=bundle.response.attributes,
            dataset=bundle.response.dataset,
        ),
        files=list(bundle.files.keys()),
    )


def _build_readme(bundle: DatasetBundle) -> str:
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
    anchoring_desc = _describe_anchoring(req)

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


def _describe_anchoring(req: DatasetBundleRequest) -> str:
    from .model import SessionAnchors, UserSuppliedAnchors

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
