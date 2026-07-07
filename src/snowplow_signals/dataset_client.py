from pydantic import BaseModel

from .api_client import ApiClient
from .models import AttributeGroup
from .models.dataset import (
    DatasetBundle,
    Output,
    SessionAnchors,
    UserSuppliedAnchors,
)


class DatasetClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def build_sql(
        self,
        attribute_groups: list[AttributeGroup],
        anchors: SessionAnchors | UserSuppliedAnchors,
        source_table: str,
        output: Output | None = None,
    ) -> DatasetBundle:
        data = {
            "source_table": source_table,
            "anchors": self._model_dump(anchors),
            "attribute_groups": [self._model_dump(ag) for ag in attribute_groups],
        }
        if output is not None:
            data["output"] = self._model_dump(output)

        response = self.api_client.make_request("POST", "datasets/sql", data=data)
        files = {f["filename"]: f["content"] for f in response["files"]}
        return DatasetBundle(files=files)

    def _model_dump(self, model: BaseModel) -> dict:
        return model.model_dump(
            mode="json",
            exclude_none=True,
            by_alias=True,
        )
