from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Field

from .connection import WarehouseConnection
from .criteria_wrapper import Criteria
from .execution import ExecutionError, ExecutionResult, StageResult
from .model import AttributeGroupInput, AttributeSqlFile
from .model import DatasetAttributeGroups as DatasetAttributeGroupsModel
from .model import DatasetBundleRequest, DatasetBundleResponse, DatasetSqlFile
from .model import SessionAnchors as SessionAnchorsModel
from .model import UserSuppliedAnchors as UserSuppliedAnchorsModel
from .model import WarehouseTable as WarehouseTableModel


class SessionAnchors(SessionAnchorsModel):
    """SDK wrapper that uses the Criteria wrapper for goal_criteria."""

    model_config = ConfigDict(populate_by_name=True)
    goal_criteria: Criteria  # type: ignore[override]


class UserSuppliedAnchors(UserSuppliedAnchorsModel):
    """SDK wrapper with populate_by_name enabled."""

    model_config = ConfigDict(populate_by_name=True)


class WarehouseTable(WarehouseTableModel):
    """SDK wrapper with populate_by_name enabled."""

    model_config = ConfigDict(populate_by_name=True)


class DatasetAttributeGroups(DatasetAttributeGroupsModel):
    """SDK wrapper with populate_by_name enabled."""

    model_config = ConfigDict(populate_by_name=True)
    attribute_groups: Sequence[AttributeGroupInput]  # type: ignore[assignment]


Anchors = Union[SessionAnchors, UserSuppliedAnchors]


class ManifestInput(BaseModel):
    anchors: dict[str, Any]
    attribute_groups: list[AttributeGroupInput]


class ManifestOutput(BaseModel):
    database: str | None
    schema_: str | None = Field(alias="schema")
    tables: dict[str, str]

    model_config = ConfigDict(populate_by_name=True)


class Manifest(BaseModel):
    generated_at: str
    input: ManifestInput
    output: ManifestOutput
    files: list[str]


class DatasetBundle(BaseModel):
    request: DatasetBundleRequest
    response: DatasetBundleResponse

    @property
    def files(self) -> dict[str, str]:
        """SQL files keyed by filename, derived from the response."""
        result: dict[str, str] = {}
        for entry in [
            self.response.anchors,
            *self.response.attributes,
            self.response.dataset,
        ]:
            if entry.sql:
                result[entry.table + ".sql"] = entry.sql
        return result

    def save_to(self, path: str | Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        for filename, content in self.files.items():
            (path / filename).write_text(content)

        manifest = self._build_manifest()
        (path / "manifest.json").write_text(
            manifest.model_dump_json(indent=2, by_alias=True) + "\n"
        )
        (path / "README.md").write_text(self._build_readme(manifest))

    def _build_manifest(self) -> Manifest:
        # Build output tables mapping
        tables: dict[str, str] = {}
        if self.response.anchors.table:
            tables["anchors"] = self.response.anchors.table
        for attr_entry in self.response.attributes:
            if attr_entry.table:
                tables[attr_entry.table] = attr_entry.table
        if self.response.dataset.table:
            tables["training_dataset"] = self.response.dataset.table

        first_entry = self.response.anchors

        return Manifest(
            generated_at=datetime.now(timezone.utc).isoformat(),
            input=ManifestInput(
                anchors=self.request.anchors.model_dump(
                    mode="json", exclude_none=True, by_alias=True
                ),
                attribute_groups=list(self.request.attributes.attribute_groups),
            ),
            output=ManifestOutput(
                database=first_entry.database,
                schema=first_entry.schema_,
                tables=tables,
            ),
            files=sorted(self.files.keys()),
        )

    def _build_readme(self, manifest: Manifest) -> str:
        lines = [
            "# Dataset SQL Bundle",
            "",
            "Generated SQL files for building a training dataset.",
            "",
            "## Files (execution order)",
            "",
        ]
        for i, filename in enumerate(sorted(self.files.keys()), 1):
            description = _file_description(filename)
            lines.append(f"{i}. `{filename}` — {description}")
        lines.append("")
        lines.append("See `manifest.json` for full configuration details.")
        lines.append("")
        return "\n".join(lines)

    def execute(self, connection: WarehouseConnection) -> ExecutionResult:
        completed_stages: list[StageResult] = []

        stages_to_run: list[
            tuple[
                Literal["anchors", "attributes", "dataset"],
                DatasetSqlFile | AttributeSqlFile,
            ]
        ] = []

        # Fixed order: anchors -> attributes -> dataset
        stages_to_run.append(("anchors", self.response.anchors))
        for attr_entry in self.response.attributes:
            stages_to_run.append(("attributes", attr_entry))
        stages_to_run.append(("dataset", self.response.dataset))

        for stage_name, entry in stages_to_run:
            table = WarehouseTable(
                database=entry.database,
                schema=entry.schema_,
                table=entry.table,
            )
            if entry.sql is None:
                continue
            try:
                connection.execute(entry.sql)
                completed_stages.append(
                    StageResult(stage=stage_name, table=table, status="completed")
                )
            except Exception as e:
                raise ExecutionError(
                    failed_stage=StageResult(
                        stage=stage_name, table=table, status="failed"
                    ),
                    completed_stages=completed_stages,
                    cause=e,
                ) from e

        # SELECT back the final training table
        dataset = self.response.dataset
        parts = [
            v
            for v in [dataset.database, dataset.schema_, dataset.table]
            if v is not None
        ]
        fqn = ".".join(parts)
        try:
            dataframe = connection.fetch_pandas(f"SELECT * FROM {fqn}")
        except Exception as e:
            raise ExecutionError(
                failed_stage=StageResult(
                    stage="dataset",
                    table=WarehouseTable(
                        database=dataset.database,
                        schema=dataset.schema_,
                        table=dataset.table,
                    ),
                    status="failed",
                ),
                completed_stages=completed_stages,
                cause=e,
            ) from e

        return ExecutionResult(dataframe=dataframe, stages=completed_stages)


def _file_description(filename: str) -> str:
    lower = filename.lower()
    if "anchor" in lower:
        return "Creates the anchor events table"
    if "attribute" in lower:
        return "Computes attributes for the anchor events"
    if "training" in lower or "dataset" in lower:
        return "Assembles the final training dataset"
    return "SQL file"
