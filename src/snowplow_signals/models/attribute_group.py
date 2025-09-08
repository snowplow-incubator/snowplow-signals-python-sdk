from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import BeforeValidator, EmailStr
from pydantic import Field
from pydantic import Field as PydanticField

from .model import (
    AttributeGroupInput,
    AttributeInput,
    AttributeKey,
    BatchSource,
    FieldModel,
    LinkAttributeKey,
)

if TYPE_CHECKING:
    from snowplow_signals.signals import Signals


def attribute_key_to_link(attribute_key: AttributeKey | LinkAttributeKey) -> LinkAttributeKey:
    if isinstance(attribute_key, AttributeKey):
        return LinkAttributeKey(name=attribute_key.name)
    return attribute_key


class AttributeGroup(AttributeGroupInput):
    attribute_key: Annotated[
        AttributeKey | LinkAttributeKey, BeforeValidator(attribute_key_to_link)
    ] = PydanticField(
        ...,
        description="The attribute key that this attribute group is associated with.",
    )  # type: ignore[assignment]
    owner: EmailStr = PydanticField(
        ...,
        description="The owner of the attribute group, typically the email of the primary maintainer. This field is required for attribute group creation.",
        title="Owner",
    )

    def get_attributes(self, signals: "Signals", identifier: str):
        """
        Retrieves the attributes for this attribute group.

        Args:
            signals: The Signals instance to use for retrieving attributes.
            identifier: The attribute key identifier to retrieve attributes for.

        Returns:
            The attributes for the attribute group.
        """

        return signals.get_group_attributes(
            name=self.name,
            version=self.version,
            attribute_key=self.attribute_key.name,
            identifier=identifier,
            attributes=[attribute.name for attribute in self.attributes],
        )


class StreamOrBatchAttributeGroup(AttributeGroup):
    fields: Literal[None] = Field(
        default=None,
        description="Not applicable.",
    )
    attributes: list[AttributeInput] = Field(
        description="The list of attributes that will be calculated from events as part of this attribute group.",
        title="Attributes",
        min_length=1,
    )


class StreamAttributeGroup(StreamOrBatchAttributeGroup):
    """
    A stream attribute group is a attribute group that is calculated from events in real-time using the Signals streaming engine.
    """

    offline: Literal[False] = Field(
        default=False,
        description="A boolean indicating whether the attributes are pre-computed in the warehouse.",
        title="Offline",
    )
    batch_source: Literal[None] = Field(
        default=None,
        description="Not applicable for stream attribute groups.",
        title="Batch Source",
    )


class BatchAttributeGroup(StreamOrBatchAttributeGroup):
    """
    A batch attribute group is a attribute group that is calculated from events in batch using the Signals batch engine.
    """

    offline: Literal[True] = Field(
        default=True,
        description="A boolean indicating whether the attributes are pre-computed in the warehouse.",
        title="Offline",
    )


class ExternalBatchAttributeGroup(AttributeGroup):
    """
    An external batch attribute group is a attribute group that is derived from an existing warehouse table.
    """

    offline: Literal[True] = Field(
        default=True,
        description="A boolean indicating whether the attributes are pre-computed in the warehouse.",
        title="Offline",
    )
    fields: list[FieldModel] = Field(
        description="The list of table columns that are part of this attribute group during materialization.",
        title="Fields",
        min_length=1,
    )
    attributes: Literal[None] = Field(
        default=None,
        description="Not applicable for warehouse table views.",
        title="Attributes",
    )
    batch_source: BatchSource = Field(
        description="The batch source for materializing this attribute group from the warehouse.",
        title="Batch Source",
    )
