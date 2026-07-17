from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Union

from pydantic import BaseModel, ConfigDict, Field

from .connection import WarehouseConnection
from .criteria_wrapper import Criteria
from .execution import ExecutionResult
from .model import AttributeGroupInput
from .model import DatasetAttributeGroups as DatasetAttributeGroupsModel
from .model import DatasetBundleRequest, DatasetBundleResponse
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


class AttributesWarehouseTable(BaseModel):
    """Optional table configuration for attribute output tables."""

    model_config = ConfigDict(populate_by_name=True)

    database: str | None = None
    schema_: str | None = Field(default=None, alias="schema")
    table_prefix: str | None = None


class DatasetAttributeGroups(DatasetAttributeGroupsModel):
    """SDK wrapper with populate_by_name enabled."""

    model_config = ConfigDict(populate_by_name=True)
    attribute_groups: Sequence[AttributeGroupInput]  # type: ignore[assignment]


Anchors = Union[SessionAnchors, UserSuppliedAnchors]


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
        from .dataset_service import save_bundle

        save_bundle(self, path)

    def execute(self, connection: WarehouseConnection) -> ExecutionResult:
        from .dataset_service import execute_bundle

        return execute_bundle(self, connection)
