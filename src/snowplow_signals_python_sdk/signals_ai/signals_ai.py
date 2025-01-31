from pydantic import BaseModel
from typing import Optional
from ..features.feature import Feature
from ..features.feature_service import FeatureService
from ..utils.utils import BrowserFeatures, make_post_request
from ..utils.types.feature_response import FeatureResponse


class SignalsAI(BaseModel):
    """Interface to interact with Snowplow Signals AI"""

    browser_features: Optional[BrowserFeatures] = None

    def get_online_features(
        self,
        features: FeatureService | list[Feature],
        entity: Optional[str] = None,
        entity_type_id: str = "domain_userid",
    ) -> FeatureResponse:

        if not entity:
            entity = getattr(self.browser_features, entity_type_id)

        headers = {"Content-Type": "application/json"}
        if isinstance(features, FeatureService):
            data = {
                "feature_service": features.name,
                "entities": {entity_type_id: [entity]},
            }
        else:
            data = {
                "features": [f"{features[0].feature_view_name}:{features[0].name}"],
                "entities": {entity_type_id: [entity]},
            }
        features = make_post_request(
            url="get-online-features", headers=headers, data=data
        )
        return FeatureResponse(**features)
