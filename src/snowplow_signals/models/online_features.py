from typing import Any

import pandas as pd
from pydantic import BaseModel


class GetOnlineFeatureResponse(BaseModel):
    data: dict[str, list[Any]]

    def to_dataframe(self):
        df = pd.DataFrame(self.data)
        return df


class GetOnlineFeaturesRequest(BaseModel):
    entities: dict[str, list[Any]]
    feature_service: str | None = None
    features: list[str] | None = None
    full_feature_names: bool = False
