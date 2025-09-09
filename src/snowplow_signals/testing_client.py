import pandas as pd

from .api_client import ApiClient
from .models import (
    TestAttributeGroupRequest,
)


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
