from typing import Annotated, List, Optional

from pydantic import BeforeValidator, Field

from .model import (
    AtomicProperty,
)
from .model import Attribute as AttributeInput
from .model import CalculatedProperty as CalculatedPropertyInput
from .model import (
    EntityProperty,
    EventLogAtomicProperty,
    EventLogEntityProperty,
    EventLogEventProperty,
    EventProperty,
)
from .model import Properties as CalculatedLeafRoot
from .model import Properties1 as EventLogPropertyRoot


def _unwrap_root(property: object) -> object:
    """Accept the generated RootModel wrapper as well as a bare property.

    `datamodel-codegen` wraps a union in a RootModel whenever it appears as a
    list item type, and names those wrappers positionally (`Properties`,
    `Properties1`, ...). A single-valued field of the same union — e.g.
    `Attribute.property` — gets the plain union with no wrapper. That
    inconsistency is an artifact of code generation, not of the API, so the SDK
    hides it: the list fields declare the union directly and this validator
    accepts either spelling, so anything that already holds a wrapper (older
    code, or a value read back from a response) keeps working.
    """
    if isinstance(property, (CalculatedLeafRoot, EventLogPropertyRoot)):
        return property.root
    return property


# One property combined by a calculated property. Same three types accepted by
# `Attribute.property`; a calculated property cannot nest another one.
_CalculatedLeaf = Annotated[
    AtomicProperty | EntityProperty | EventProperty,
    BeforeValidator(_unwrap_root),
]

# One property projected from a matched event, within an event log.
_EventLogProperty = Annotated[
    EventLogAtomicProperty | EventLogEntityProperty | EventLogEventProperty,
    BeforeValidator(_unwrap_root),
]


class CalculatedProperty(CalculatedPropertyInput):
    """A single value derived from several other properties on the same event."""

    properties: List[_CalculatedLeaf] = Field(  # type: ignore[assignment]
        ...,
        description=(
            "The properties to combine, in order. A flat list of leaf properties — "
            "a calculated property cannot contain another calculated property."
        ),
        max_length=50,
        min_length=1,
    )


class Attribute(AttributeInput):
    """An attribute computed from matching events.

    Overrides `property` only to admit the `CalculatedProperty` subclass above:
    the generated annotation names the generated class, so passing the wrapper
    would serialize correctly but emit a pydantic "unexpected value" warning on
    every dump.
    """

    property: Optional[  # type: ignore[assignment]
        AtomicProperty | EventProperty | EntityProperty | CalculatedProperty
    ] = Field(
        default=None,
        description=(
            "The path to the property on the event or entity you wish to use in "
            "the aggregation."
        ),
    )
