from typing import Annotated

from pydantic import BeforeValidator, Field

from .model import AttributeInput
from .property_wrappers.atomic import AtomicProperty
from .property_wrappers.entity import EntityProperty
from .property_wrappers.event import EventProperty


def convert_property_wrapper_to_string(
    value: EventProperty | EntityProperty | AtomicProperty | None,
) -> str | None:
    if isinstance(value, str):
        return value

    if value is None:
        return None

    if isinstance(value, (EventProperty, EntityProperty, AtomicProperty)):
        return value._to_api_property()

    raise ValueError(
        f"property must be a string, wrapper object, or None, got {type(value)}"
    )


class Attribute(AttributeInput):
    property: Annotated[str | EventProperty | EntityProperty | AtomicProperty | None, BeforeValidator(convert_property_wrapper_to_string)] = Field(default=None, description="The property on the event or entity to use in the aggregation.")  # type: ignore[assignment]
