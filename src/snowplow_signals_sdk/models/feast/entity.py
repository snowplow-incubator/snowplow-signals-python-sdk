from typing import Optional

from pydantic import BaseModel
from pydantic import Field as PydanticField

from snowplow_signals_sdk.api_client import ApiClient
from snowplow_signals_sdk.models.types import ValueType

from .base_feast_object import BaseFeastObject


class Field(BaseModel):
    """
    A Field represents a set of values with the same structure.
    """

    name: str = PydanticField(description="The name of the field.")

    description: str | None = PydanticField(
        description="A human-readable description.",
        default=None,
    )

    dtype: ValueType = PydanticField(
        description="The type of the field, such as string or float.",
        default="UNKNOWN",
    )

    tags: dict[str, str] | None = PydanticField(
        description="A dictionary of key-value pairs to store arbitrary metadata.",
        default=None,
    )

    vector_index: bool = PydanticField(
        description="If set to True the field will be indexed for vector similarity search.",
        default=False,
    )

    vector_search_metric: str | None = PydanticField(
        description="The metric used for vector similarity search.",
        default=None,
    )


class Entity(BaseFeastObject):
    """
    Defines entities for which features can be defined.
    An entity can also contain associated metadata.
    """

    join_keys: list[str] | None = PydanticField(
        description="""
        A property that uniquely identifies different entities within the
        collection. The join_key property is typically used for joining entities
        with their associated features. If not specified, defaults to the name.
        """,
        default=None,
    )

    value_type: ValueType = PydanticField(
        description="The type of the entity, such as string or float.",
        default="UNKNOWN",
    )

    def register_to_store(self, api_client: ApiClient) -> Optional["Entity"]:
        if self.already_registered(api_client=api_client, object_type="entities"):
            return self

        response = api_client.make_post_request(
            endpoint="registry/entities/", data=self.model_dump(mode="json")
        )
        self.id = response.get("_id", self.id)
        return self
