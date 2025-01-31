from pydantic import BaseModel


class Feature(BaseModel):
    feature_view_name: str
    name: str
