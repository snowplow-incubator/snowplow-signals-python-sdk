from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import Field as PydanticField

from snowplow_signals.api_client import ApiClient


class BaseSignalsObject(BaseModel):
    """
    BaseSignalsObject is an interface for other Signals objects. ie Features, FeatureViews and Entities.
    """

    name: str = PydanticField(
        description="Name of the Signals Object.",
    )

    applied_at: datetime | None = PydanticField(
        description="Timestamp indicating the last time the model was applied to Signals.",
        default=None,
    )

    description: str | None = PydanticField(
        description="A human-readable description.",
        default=None,
    )

    tags: dict[str, str] | None = PydanticField(
        description="A dictionary of key-value pairs to store arbitrary metadata.",
        default=None,
    )

    owner: str | None = PydanticField(
        description="The owner of the object, typically the email of the primary maintainer.",
        default=None,
    )

    def register_to_store(self, api_client: ApiClient) -> Optional["BaseSignalsObject"]:
        raise NotImplementedError("register_to_store is not implemented")
