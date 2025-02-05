from pydantic import BaseModel


class FeatureService(BaseModel):
    name: str
