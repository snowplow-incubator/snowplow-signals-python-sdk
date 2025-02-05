from pydantic import BaseModel


class FeatureView(BaseModel):
    feature_view_name: str
    name: str
