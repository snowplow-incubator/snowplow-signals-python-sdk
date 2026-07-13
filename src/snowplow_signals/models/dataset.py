from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Union

from pydantic import BaseModel, ConfigDict

from .criteria_wrapper import Criteria
from .model import DatasetAttributeGroups as DatasetAttributeGroupsModel
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


Anchors = Union[SessionAnchors, UserSuppliedAnchors]


class DatasetBundle(BaseModel):
    files: dict[str, str]
    request_data: dict[str, Any] = {}
    response_data: dict[str, Any] = {}

    def save_to(self, path: str | Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        for filename, content in self.files.items():
            (path / filename).write_text(content)

        manifest = self._build_manifest()
        (path / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        (path / "README.md").write_text(self._build_readme(manifest))

    def _build_manifest(self) -> dict[str, Any]:
        response = self.response_data
        request = self.request_data

        # Build output tables mapping
        tables: dict[str, str] = {}
        anchors_entry = response.get("anchors", {})
        if anchors_entry.get("table"):
            tables["anchors"] = anchors_entry["table"]
        for attr_entry in response.get("attributes", []):
            if attr_entry.get("table"):
                tables[attr_entry["table"]] = attr_entry["table"]
        dataset_entry = response.get("dataset", {})
        if dataset_entry.get("table"):
            tables["training_dataset"] = dataset_entry["table"]

        # Determine output database/schema from response
        first_entry = anchors_entry or dataset_entry or {}
        output_db = first_entry.get("database")
        output_schema = first_entry.get("schema")

        # Build attribute group summaries
        attr_groups = []
        for ag in request.get("attributes", {}).get("attribute_groups", []):
            attr_groups.append(
                {
                    "name": ag.get("name"),
                    "version": ag.get("version", 1),
                }
            )

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "input": {
                "anchors": request.get("anchors", {}),
                "attribute_groups": attr_groups,
            },
            "output": {
                "database": output_db,
                "schema": output_schema,
                "tables": tables,
            },
            "files": sorted(self.files.keys()),
        }

    def _build_readme(self, manifest: dict[str, Any]) -> str:
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


def _file_description(filename: str) -> str:
    lower = filename.lower()
    if "anchor" in lower:
        return "Creates the anchor events table"
    if "attribute" in lower:
        return "Computes attributes for the anchor events"
    if "training" in lower or "dataset" in lower:
        return "Assembles the final training dataset"
    return "SQL file"
