from typing import Optional, Union

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
        if self.already_registered(
            api_client=api_client, object_type="feature_services"
        ):
            return self

        for i, fv in enumerate(self.feature_views):
            updated_fv = fv.register_to_store(api_client=api_client)

            if updated_fv:
                self.feature_views[i] = updated_fv
                fv.id = updated_fv.id
            if not fv.id:
                raise ValueError(f"Feature view {fv.name} has no property: id")

        request_data = FeatureService.model_validate(self.model_dump())
        request_data.feature_views = [fv.id for fv in self.feature_views]

        response = api_client.make_post_request(
            endpoint="registry/feature_services/",
            data=request_data.model_dump(mode="json"),
        )

        self.id = response.get("_id", self.id)

        return self
