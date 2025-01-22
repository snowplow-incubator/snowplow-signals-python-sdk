from pydantic import BaseModel, ConfigDict
from typing import  Self, Optional, Any
import json


class FeatureDict(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    @classmethod
    def initialize(
        cls, 
        data: dict
    ) -> Self:
        return cls(**data)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self.dict().get(key, default)

class SignalsAI(BaseModel):
    """Interface to interact with Snowplow Signals AI"""
    
    def get_features_from_cookie(self, cookie: str) -> FeatureDict:
        cookies_dict = json.loads(cookie)
        return FeatureDict.initialize(data=cookies_dict)