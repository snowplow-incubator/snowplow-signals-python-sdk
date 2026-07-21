from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Union

from pydantic import BaseModel, ConfigDict, Field

from .connection import WarehouseConnection
from .criteria_wrapper import Criteria
from .execution import ExecutionResult
from .model import AttributeGroupInput, AttributeSqlFile
from .model import DatasetAttributeGroups as DatasetAttributeGroupsModel
from .model import DatasetBundleRequest, DatasetBundleResponse, DatasetSqlFile
from .model import SessionAnchors as SessionAnchorsModel
from .model import UserSuppliedAnchors as UserSuppliedAnchorsModel
from .model import WarehouseTable as WarehouseTableModel

if TYPE_CHECKING:
    from snowplow_signals.dataset_client import DatasetClient


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


class ManifestDefinition(BaseModel):
    anchors: Union[SessionAnchorsModel, UserSuppliedAnchorsModel] = Field(
        discriminator="mode"
    )
    attribute_groups: list[AttributeGroupInput]


class ManifestTables(BaseModel):
    anchors: DatasetSqlFile
    attributes: list[AttributeSqlFile]
    dataset: DatasetSqlFile


class Manifest(BaseModel):
    generated_at: str
    definition: ManifestDefinition
    tables: ManifestTables
    files: list[str]


class DatasetBundle(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    request: DatasetBundleRequest
    response: DatasetBundleResponse
    _dataset_client: DatasetClient | None = None

    def __init__(
        self,
        *,
        request: DatasetBundleRequest,
        response: DatasetBundleResponse,
        dataset_client: DatasetClient | None = None,
    ) -> None:
        super().__init__(request=request, response=response)
        self._dataset_client = dataset_client

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
        if self._dataset_client is None:
            raise RuntimeError(
                "save_to requires a DatasetClient. "
                "Use the bundle returned by Signals.build_dataset_with_*()."
            )
        self._dataset_client.save_dataset_bundle(self, path)

    def execute(self, connection: WarehouseConnection) -> ExecutionResult:
        if self._dataset_client is None:
            raise RuntimeError(
                "execute requires a DatasetClient. "
                "Use the bundle returned by Signals.build_dataset_with_*()."
            )
        return self._dataset_client.execute_dataset_bundle(self, connection)
