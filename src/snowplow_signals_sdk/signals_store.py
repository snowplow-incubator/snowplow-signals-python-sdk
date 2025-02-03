from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union
from .models.feature_view import FeatureView
from .models.feature_service import FeatureService
from .models.browser_features import BrowserFeatures
from .utils import make_post_request
from .models.feature_response import FeatureResponse
from .api_client.api_client import ApiClient, DEFAULT_API_CLIENT


class SignalsStore(BaseModel):
    """Interface to interact with Snowplow Signals AI"""

    browser_features: Optional[BrowserFeatures] = None
    api_client: ApiClient = DEFAULT_API_CLIENT

    def get_online_features(
        self,
        features: Union[FeatureService, list[FeatureView]],
        entity: Optional[str] = None,
        entity_type_id: str = "domain_userid",
    ) -> FeatureResponse:

        entity = entity or getattr(self.browser_features, entity_type_id, None)
        if entity is None:
            raise ValueError(f"Entity `{entity_type_id}` could not be determined.")

        if not features:
            return None

        if isinstance(features, FeatureService):
            data = {
                "feature_service": features.name,
                "entities": {entity_type_id: [entity]},
            }
        elif isinstance(features, list[FeatureView]):
            data = {
                "features": [f"{f.feature_view_name}:{f.name}" for f in features],
                "entities": {entity_type_id: [entity]},
            }
        else:
            raise TypeError(
                "Features must be a FeatureService or a list of FeatureView."
            )

        response = self.api_client.make_post_request(
            endpoint="/get-online-features/", data=data
        )
        return FeatureResponse(**response) if response else None
