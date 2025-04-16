import json
from pydantic import BaseModel, model_validator, ValidationError
from typing import Optional
import logging

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

    @classmethod
    def from_path(
        cls, config_path: str, table_name: str
    ) -> Optional["BatchSourceConfig"]:
        try:
            with open(config_path) as f:
                data = json.load(f)
            return cls(**data)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"❌ Error loading batch source config: {str(e)}")
        except ValidationError as e:
            logger.error(f"❌ Config validation error for {table_name}:\n{e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error for {table_name}: {e}")
        return None
