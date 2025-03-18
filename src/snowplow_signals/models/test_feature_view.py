from datetime import timedelta

from pydantic import BaseModel
from .feature_view import FeatureView


class TestFeatureViewRequest(BaseModel):
    feature_view: FeatureView
    app_ids: list[str] = []
    window: timedelta = timedelta(hours=1)
    entity_ids: list[str]
