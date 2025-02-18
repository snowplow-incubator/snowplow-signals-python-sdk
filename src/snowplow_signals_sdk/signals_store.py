from typing import Any, Literal, Optional, Union

from pydantic import BaseModel

from .api_client import DEFAULT_API_CLIENT, ApiClient
from .models.feast.base_feast_object import BaseFeastObject
from .models.feast.feature_service import FeatureService
from .models.feast.feature_view import FeatureView
from .models.feast.entity import Entity
from .models.feast.data_source import DataSource
from .models.online_feature_response import OnlineFeatureResponse


class ApplyResponse(BaseModel):
    status: Literal["applied", "nothing to apply"]


class GetOnlineFeaturesRequest(BaseModel):
    entities: dict[str, list[Any]]
    feature_service: str | None = None
    features: list[str] | None = None
    full_feature_names: bool = False


class SignalsStore(BaseModel):
    """Interface to interact with Snowplow Signals AI"""

    api_client: ApiClient = DEFAULT_API_CLIENT

    def apply(self, objects: Optional[list[BaseFeastObject]] = None) -> "ApplyResponse":
        if objects:
            # We need to register first entities, then data_sources, then feature_views and finally feature_services to handle dependencies
            entities = [object for object in objects if isinstance(object, Entity)]
            for entity in entities:
                entity.register_to_store(api_client=self.api_client)

            data_sources = [
                object for object in objects if isinstance(object, DataSource)
            ]
            for data_source in data_sources:
                data_source.register_to_store(api_client=self.api_client)

            feature_views = [
                object for object in objects if isinstance(object, FeatureView)
            ]
            for feature_view in feature_views:
                feature_view.register_to_store(api_client=self.api_client)

            feature_services = [
                object for object in objects if isinstance(object, FeatureService)
            ]
            for feature_service in feature_services:
                feature_service.register_to_store(api_client=self.api_client)

        response = self.api_client.make_post_request(
            endpoint="feature_store/apply",
        )
        return ApplyResponse(**response)

    def get_online_features(
        self,
        features: Union[FeatureService, list[FeatureView]],
        entity: Optional[str] = None,
        entity_type_id: str = "domain_userid",
    ) -> Optional[OnlineFeatureResponse]:

        if entity is None:
            raise ValueError(f"Entity `{entity_type_id}` could not be determined.")

        if not features:
            raise ValueError(f"No Features to fetch.")

        if isinstance(features, FeatureService):
            data = GetOnlineFeaturesRequest(
                feature_service=features.name,
                entities={entity_type_id: [entity]},
            )

        elif all(isinstance(fv, FeatureView) for fv in features):
            feature_names = [
                f"{fv.feast_name}:{feature.name}"
                for fv in features
                for feature in fv.features + fv.fields
            ]
            data = GetOnlineFeaturesRequest(
                features=feature_names,
                entities={entity_type_id: [entity]},
            )
        else:
            raise TypeError(
                "Features must be a FeatureService or a list of FeatureView."
            )
        response = self.api_client.make_post_request(
            endpoint="get-online-features", data=data.model_dump(mode="json")
        )
        return OnlineFeatureResponse(data=response) if response else None
