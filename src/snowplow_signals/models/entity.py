from typing import Optional

from pydantic import Field as PydanticField

from snowplow_signals.api_client import ApiClient, NotFoundException
from snowplow_signals.models.types import ValueType

from .base_signals_object import BaseSignalsObject


class Entity(BaseSignalsObject):
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
        try:
            response = api_client.make_request(
                method="GET", endpoint=f"registry/entities/{self.name}"
            )
        except NotFoundException:
            response = api_client.make_request(
                method="POST",
                endpoint="registry/entities/",
                data=self.model_dump(mode="json"),
            )

        response = Entity.model_validate(response)
        self.__dict__.update(response)
        return self


# Predefined entities
user_entity = Entity(name="user", value_type="STRING")
session_entity = Entity(name="session", value_type="STRING")
