from __future__ import annotations

from pydantic import BaseModel

from .api_client import ApiClient
from .models import (
    Anchors,
    AttributeGroup,
    DatasetAttributeGroups,
    DatasetBundle,
    WarehouseTable,
)
from .models.model import DatasetBundleRequest, DatasetBundleResponse


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
        request = DatasetBundleRequest(
            anchors=anchors,
            attributes=DatasetAttributeGroups(
                attribute_groups=attribute_groups,
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
        )

    def _model_dump(self, model: BaseModel) -> dict:
        return model.model_dump(
            mode="json",
            exclude_none=True,
            by_alias=True,
        )
