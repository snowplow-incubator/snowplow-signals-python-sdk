from typing import Any, List, Optional

import pandas as pd
from pydantic import BaseModel


class Metadata(BaseModel):
    feature_names: List[str]


class Result(BaseModel):
    values: List[Optional[Any]]
    statuses: List[str]
    event_timestamps: List[str]


class FeatureResponse(BaseModel):
    metadata: Metadata
    results: List[Result]

    def to_dataframe(self):
        values = [result.values for result in self.results]
        df = pd.DataFrame(list(zip(*values)), columns=self.metadata.feature_names)
        return df
