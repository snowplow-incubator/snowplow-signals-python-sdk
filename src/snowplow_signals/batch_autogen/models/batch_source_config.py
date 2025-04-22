from pydantic import BaseModel, model_validator, ValidationError
import logging
from typing import Self, Dict, Any

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
    def validate_config(cls, values):
        ts = values.timestamp_field
        created_ts = values.created_timestamp_column

        if ts == created_ts:
            raise ValueError(
                "timestamp_field and created_timestamp_column should not be the same."
            )
        return values
