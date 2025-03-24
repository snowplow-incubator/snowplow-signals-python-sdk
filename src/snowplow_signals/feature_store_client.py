from .api_client import ApiClient


class FeatureStoreClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def apply(self) -> None:
        self.api_client.make_request(
            method="POST",
            endpoint="feature_store/apply",
        )
