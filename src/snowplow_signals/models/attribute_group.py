from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import BeforeValidator, EmailStr
from pydantic import Field
from pydantic import Field as PydanticField

from .attribute_key import AttributeKey
from .model import Attribute as AttributeInput
from .model import (
    AttributeGroupInput,
    AttributeGroupResponse,
    BatchSource,
    FieldModel,
    LinkAttributeKey,
    SourceGroupReference,
)

if TYPE_CHECKING:
    from snowplow_signals.signals import Signals


def attribute_key_link_to_attribute_key(
    attribute_key: AttributeKey | LinkAttributeKey,
) -> AttributeKey:
    if isinstance(attribute_key, LinkAttributeKey):
        return AttributeKey(name=attribute_key.name)
    return attribute_key


class AttributeGroup(AttributeGroupInput):
    attribute_key: Annotated[
        AttributeKey | LinkAttributeKey,
        BeforeValidator(attribute_key_link_to_attribute_key),
    ] = PydanticField(  # type: ignore[assignment]
        ...,
        description="The attribute key that this attribute group is associated with.",
    )
    owner: EmailStr = PydanticField(
        ...,
        description="The owner of the attribute group, typically the email of the primary maintainer. This field is required for attribute group creation.",
        title="Owner",
    )

    def attribute_reference(self, attribute_name: str) -> SourceGroupReference:
        """
        Returns a reference to one of this attribute group's attributes, for use as
        an input attribute of a predictive attribute.

        Args:
            attribute_name: The name of the attribute.

        Returns:
            A reference to the attribute in this version of the attribute group.
        """
        return attribute_reference(self, attribute_name)

    def get_attributes(self, signals: "Signals", identifier: str):
        """
        Retrieves the attributes for this attribute group.

        Args:
            signals: The Signals instance to use for retrieving attributes.
            identifier: The attribute key identifier to retrieve attributes for.

        Returns:
            The attributes for the attribute group.
        """

        attributes = [
            attribute.name
            for attribute in (self.attributes or []) + (self.fields or [])
        ]

        return signals.get_group_attributes(
            name=self.name,
            version=self.version,  # type: ignore[arg-type]
            attribute_key=self.attribute_key.name,  # type: ignore[arg-type]
            identifier=identifier,
            attributes=attributes,
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


def attribute_reference(
    attribute_group: AttributeGroup | AttributeGroupResponse, attribute_name: str
) -> SourceGroupReference:
    """
    Returns a reference to an attribute of an attribute group, for use as an input
    attribute of a predictive attribute.

    Args:
        attribute_group: The stream attribute group, as defined or as fetched from the registry.
        attribute_name: The name of the attribute.

    Returns:
        A reference to the attribute in this version of the attribute group.
    """
    if attribute_group.offline:
        raise ValueError(
            f"Attribute group '{attribute_group.name}' is computed in the warehouse; "
            "predictive attributes can only use attributes of stream attribute groups."
        )
    names = [attribute.name for attribute in attribute_group.attributes or []]
    if attribute_name not in names:
        raise ValueError(
            f"Attribute '{attribute_name}' not found in attribute group "
            f"'{attribute_group.name}' (v{attribute_group.version})."
        )
    if attribute_group.version is None:
        raise ValueError(f"Attribute group '{attribute_group.name}' has no version.")
    return SourceGroupReference(
        name=attribute_group.name,
        version=attribute_group.version,
        attribute_name=attribute_name,
    )
