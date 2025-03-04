from typing import Literal, Optional, Union
from datetime import timedelta
import pandas as pd

from pydantic import BaseModel

from .api_client import ApiClient
from .models.base_signals_object import BaseSignalsObject
from .models.feature_service import FeatureService
from .models.feature_view import FeatureView
from .models.online_features import GetOnlineFeatureResponse, GetOnlineFeaturesRequest
from .models.test_feature_view import TestFeatureViewRequest
from .prompts.client import PromptsClient


class ApplyResponse(BaseModel):
    status: Literal["applied", "nothing to apply"]


class Signals:
    """Interface to interact with Snowplow Signals AI"""

    def __init__(self, api_url: str):
        self.api_client = ApiClient(api_url=api_url)
        self.prompts = PromptsClient(api_client=self.api_client)

    def apply(
        self, objects: Optional[list[BaseSignalsObject]] = None
    ) -> "ApplyResponse":
        if objects:
            for object in objects:
                object.register_to_store(api_client=self.api_client)

        response = self.api_client.make_request(
            method="POST",
            endpoint="feature_store/apply",
        )
        return ApplyResponse(**response)

    def get_online_features(
        self,
        features: Union[FeatureService, list[FeatureView]],
        entity: Optional[str] = None,
        entity_type_id: str = "domain_userid",
    ) -> Optional[GetOnlineFeatureResponse]:

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
        response = self.api_client.make_request(
            method="POST",
            endpoint="get-online-features",
            data=data.model_dump(mode="json"),
        )
        return GetOnlineFeatureResponse(data=response) if response else None

    def test(
        self,
        feature_view: FeatureView,
        entity_ids: list[str] = [],
        app_ids: list[str] = [],
        window: timedelta = timedelta(hours=1),
    ) -> pd.DataFrame:
        """
        Tests the feature view by extracting the features from the latest window of events in the atomic events table in warehouse.

        Args:
            feature_view: The feature view to test.
            entity_ids: The list of entity ids (e.g., domain_userid values) to extract features for. If empty, random 10 IDs will be used.
            app_ids: The list of app ids to extract features for.
            window: The time window to extract features from.
        """
        request = TestFeatureViewRequest(
            feature_view=feature_view,
            entity_ids=entity_ids,
            window=window,
            app_ids=app_ids,
        )

        data = self.api_client.make_post_request(
            endpoint="testing/feature_views/",
            data=request.model_dump(mode="json"),
        )

        return pd.DataFrame(data)
