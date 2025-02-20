from typing import Any, List, Optional

import pandas as pd
from pydantic import BaseModel


class Metadata(BaseModel):
    feature_names: List[str]


class Result(BaseModel):
    values: List[Optional[Any]]
    statuses: List[str]
    event_timestamps: List[str]


class OnlineFeatureResponse(BaseModel):
    data: dict[str, list[Any]]

    def to_dataframe(self):
        df = pd.DataFrame(self.data)
        return df
