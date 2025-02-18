from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel
from pydantic import Field as PydanticField

from snowplow_signals_sdk.api_client import ApiClient


class BaseFeastObject(BaseModel):
    """
    BaseFeastObject is an interface for other Feast objects. ie Features, FeatureViews and Entities.
    """

    name: str = PydanticField(
        description="Name of the Feast Object.",
    )

    applied_at: datetime | None = PydanticField(
        description="Timestamp indicating the last time the model was applied to Feast.",
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

    def register_to_store(self, api_client: ApiClient) -> Optional["BaseFeastObject"]:
        raise NotImplementedError("register_to_store is not implemented")

    def already_registered(
        self,
        api_client: ApiClient,
        object_type: Literal[
            "feature_services", "feature_views", "entities", "data_sources"
        ],
        version: Optional[int] = None,
    ) -> bool:
        url = (
            f"registry/{object_type}/{self.name}/versions/{version}"
            if version
            else f"registry/{object_type}/{self.name}"
        )
        exists = api_client.make_get_request(endpoint=url)
        return "detail" not in exists
