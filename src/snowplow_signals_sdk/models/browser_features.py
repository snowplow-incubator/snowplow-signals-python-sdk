from typing import Self

from pydantic import BaseModel


class BrowserFeatures(BaseModel):
    domain_userid: str
    domain_sessionidx: str
    domain_sessionid: str

    @classmethod
    def initialize(cls, data: dict) -> Self:
        return cls(**data)
