import logging

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class BatchSourceConfig(BaseModel):
    database: str
    wh_schema: str
    table: str
    name: str
    timestamp_field: str
    description: str | None
    tags: dict[str, str] | None
    owner: str | None
