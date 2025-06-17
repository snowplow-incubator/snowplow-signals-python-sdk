from typing import TYPE_CHECKING, Annotated

from pydantic import BeforeValidator, EmailStr, Field

from .model import Service as ServiceInput
from .model import VersionedLinkView
from .view import View

if TYPE_CHECKING:
    from snowplow_signals.signals import Signals


def view_to_link(
    views: list[View | VersionedLinkView | dict] | None,
) -> list[VersionedLinkView | dict] | None:
    if views:
        views = [
            (
                VersionedLinkView(name=view.name, version=view.version)
                if isinstance(view, View)
                else view
            )
            for view in views
        ]
    return views


class Service(ServiceInput):
    views: Annotated[list[VersionedLinkView | View], BeforeValidator(view_to_link)] = (
        Field(
            None,
            description="A list containing views, representing the features in the service.",
            max_length=100,
            min_length=1,
            title="Views",
        )  # type: ignore[assignment]
    )
    owner: EmailStr = Field(
        ...,
        description="The owner of the service, typically the email of the primary maintainer. This field is required for service creation.",
        title="Owner",
    )

    def get_attributes(
        self, signals: "Signals", identifiers: list[str] | str, entity: str
    ):
        """
        Retrieves the online attributes for this service.

        Args:
            signals: The Signals instance to use for retrieving attributes.
            identifiers: The list of entity identifiers to retrieve attributes for.
            entity: The entity name to retrieve attributes for.

        Returns:
            The online attributes for the service.
        """

        return signals.attributes.get_service_attributes(
            name=self.name,
            entity=entity,
            identifiers=identifiers,
        )
