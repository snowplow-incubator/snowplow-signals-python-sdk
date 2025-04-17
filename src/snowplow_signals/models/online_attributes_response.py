from typing import Any

import pandas as pd
from pydantic import BaseModel


class OnlineAttributesResponse(BaseModel):
    data: dict[str, list[Any]]

    def to_dataframe(self):
        df = pd.DataFrame(self.data)
        return df
