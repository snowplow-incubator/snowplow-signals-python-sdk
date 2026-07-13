from __future__ import annotations

from pydantic import BaseModel

from .api_client import ApiClient
from .models import (
    Anchors,
    AttributeGroup,
    DatasetBundle,
    WarehouseTable,
)


class DatasetClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def build_sql(
        self,
        attribute_groups: list[AttributeGroup],
        anchors: Anchors,
        attributes_database: str | None = None,
        attributes_schema: str | None = None,
        attributes_table_prefix: str | None = None,
        dataset: WarehouseTable | None = None,
        max_lookback_days: int | None = None,
    ) -> DatasetBundle:
        attributes_data: dict = {
            "attribute_groups": [self._model_dump(ag) for ag in attribute_groups],
        }
        if attributes_database is not None:
            attributes_data["database"] = attributes_database
        if attributes_schema is not None:
            attributes_data["schema"] = attributes_schema
        if attributes_table_prefix is not None:
            attributes_data["table_prefix"] = attributes_table_prefix

        data: dict = {
            "anchors": self._model_dump(anchors),
            "attributes": attributes_data,
        }
        if dataset is not None:
            data["dataset"] = self._model_dump(dataset)
        if max_lookback_days is not None:
            data["max_lookback_days"] = max_lookback_days

        response = self.api_client.make_request("POST", "datasets/sql", data=data)
        files = {}
        for section in ("anchors", "dataset"):
            entry = response.get(section)
            if entry and entry.get("sql"):
                files[entry["table"] + ".sql"] = entry["sql"]
        for entry in response.get("attributes", []):
            if entry.get("sql"):
                files[entry["table"] + ".sql"] = entry["sql"]
        return DatasetBundle(
            files=files,
            request_data=data,
            response_data=response,
        )

    def _model_dump(self, model: BaseModel) -> dict:
        return model.model_dump(
            mode="json",
            exclude_none=True,
            by_alias=True,
        )
