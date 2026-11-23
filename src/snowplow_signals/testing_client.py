import pandas as pd

from .api_client import ApiClient
from .models import PredictiveAttributeTestResponse, TestAttributeGroupRequest
from .models.model import TestPredictiveAttributeRequest


class TestingClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def test_attribute_group(self, request: TestAttributeGroupRequest) -> pd.DataFrame:
        data = self.api_client.make_request(
            method="POST",
            endpoint="testing/attribute_groups/",
            data=request.model_dump(
                mode="json",
                exclude_none=True,
            ),
        )

        return pd.DataFrame(data)

    def test_predictive_attribute(
        self, request: TestPredictiveAttributeRequest
    ) -> PredictiveAttributeTestResponse:
        data = self.api_client.make_request(
            method="POST",
            endpoint="testing/predictive_attributes/",
            data=request.model_dump(
                mode="json",
                exclude_none=True,
                by_alias=True,
            ),
        )

        return PredictiveAttributeTestResponse.model_validate(data)
