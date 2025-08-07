import logging
from typing import Self

from pydantic import BaseModel, model_validator

logger = logging.getLogger(__name__)


class BatchSourceConfig(BaseModel):
    database: str
    wh_schema: str
    table: str
    name: str
    timestamp_field: str
    created_timestamp_column: str
    description: str | None
    tags: dict[str, str] | None
    owner: str | None

    @model_validator(mode="after")
    def validate_config(self) -> Self:
        if self.timestamp_field == self.created_timestamp_column:
            raise ValueError(
                "timestamp_field and created_timestamp_column should not be the same."
            )
        return self
