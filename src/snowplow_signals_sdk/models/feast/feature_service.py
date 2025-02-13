from typing import Optional

from pydantic import Field as PydanticField

from snowplow_signals_sdk.api_client import ApiClient

from .base_feast_object import BaseFeastObject
from .feature_view import FeatureView


class FeatureService(BaseFeastObject):
    """
    A feature service defines a logical group of features from one or more feature views.
    This group of features can be retrieved together during training or serving.
    """

    name: str
    feature_views: list[FeatureView] = PydanticField(
        description="A list containing feature views and feature view projections, representing the features in the feature service.",
        default=[],
    )

    def register_to_store(self, api_client: ApiClient) -> Optional["FeatureService"]:
        response = api_client.make_post_request(
            endpoint="registry/feature_services/", data=self.model_dump(mode="json")
        )
        # If data source is already registered return None
        if response.get("detail"):
            return None

        return FeatureService.model_validate(response)
