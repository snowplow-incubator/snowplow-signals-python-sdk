from typing import Any

from pydantic import BaseModel


class GetAttributesResponse(BaseModel):
    data: dict[str, list[Any]]
