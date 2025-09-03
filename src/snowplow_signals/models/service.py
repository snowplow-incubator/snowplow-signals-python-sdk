from typing import TYPE_CHECKING, Annotated

from pydantic import BeforeValidator, EmailStr, Field

from .model import Service as ServiceInput
from .model import VersionedLinkAttributeGroup
from .view import AttributeGroup

if TYPE_CHECKING:
    from snowplow_signals.signals import Signals


def view_to_link(
    views: list[AttributeGroup | VersionedLinkAttributeGroup | dict] | None,
) -> list[VersionedLinkAttributeGroup | dict] | None:
    if views:
        views = [
            (
                VersionedLinkAttributeGroup(name=view.name, version=view.version)
                if isinstance(view, AttributeGroup)
                else view
            )
            for view in views
        ]
    return views


class Service(ServiceInput):
    views: Annotated[
        list[VersionedLinkAttributeGroup | AttributeGroup],
        BeforeValidator(view_to_link),
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

    def get_attributes(self, signals: "Signals", entity: str, identifier: str):
        """
        Retrieves the attributes for this service.

        Args:
            signals: The Signals instance to use for retrieving attributes.
            entity: The attribute key to retrieve attributes for.
            identifier: The attribute key identifier to retrieve attributes for.

        Returns:
            The attributes for the service.
        """

        return signals.attributes.get_service_attributes(
            name=self.name,
            entity=entity,
            identifier=identifier,
        )
