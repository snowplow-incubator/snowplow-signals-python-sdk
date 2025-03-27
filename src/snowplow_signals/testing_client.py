import pandas as pd
from .api_client import ApiClient
from .models import (
    TestViewRequest,
)


class TestingClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def test_view(self, request: TestViewRequest) -> pd.DataFrame:
        data = self.api_client.make_request(
            method="POST",
            endpoint="testing/views/",
            data=request.model_dump(
                mode="json",
                exclude_none=True,
            ),
        )

        return pd.DataFrame(data)
