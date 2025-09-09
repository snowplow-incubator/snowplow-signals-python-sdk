from typing import TYPE_CHECKING, Annotated

from pydantic import BeforeValidator, EmailStr, Field

from .model import Service as ServiceInput
from .model import VersionedLinkAttributeGroup
from .attribute_group import AttributeGroup

if TYPE_CHECKING:
    from snowplow_signals.signals import Signals


def attribute_group_to_link(
    attribute_groups: list[AttributeGroup | VersionedLinkAttributeGroup | dict] | None,
) -> list[VersionedLinkAttributeGroup | dict] | None:
    if attribute_groups:
        attribute_groups = [
            (
                VersionedLinkAttributeGroup(name=attribute_group.name, version=attribute_group.version)
                if isinstance(attribute_group, AttributeGroup)
                else attribute_group
            )
            for attribute_group in attribute_groups
        ]
    return attribute_groups


class Service(ServiceInput):
    attribute_groups: Annotated[
        list[VersionedLinkAttributeGroup | AttributeGroup],
        BeforeValidator(attribute_group_to_link),
    ] = Field(
        None,
        description="A list containing Attribute Groups, representing the features in the service.",
        max_length=100,
        min_length=1,
        title="Attribute Groups",
    )  # type: ignore[assignment]
    owner: EmailStr = Field(
        ...,
        description="The owner of the service, typically the email of the primary maintainer. This field is required for service creation.",
        title="Owner",
    )

    def get_attributes(self, signals: "Signals", attribute_key: str, identifier: str):
        """
        Retrieves the attributes for this service.

        Args:
            signals: The Signals instance to use for retrieving attributes.
            attribute_key: The attribute key to retrieve attributes for.
            identifier: The attribute key identifier to retrieve attributes for.

        Returns:
            The attributes for the service.
        """

        return signals.attributes.get_service_attributes(
            name=self.name,
            attribute_key=attribute_key,
            identifier=identifier,
        )
