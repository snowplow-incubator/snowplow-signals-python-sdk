from typing import TYPE_CHECKING, Annotated

from pydantic import BeforeValidator, EmailStr
from pydantic import Field as PydanticField

from .model import (
    Entity,
    LinkEntity,
    ViewInput,
)

if TYPE_CHECKING:
    from snowplow_signals.signals import Signals


def entity_to_link(entity: Entity | LinkEntity) -> LinkEntity:
    if isinstance(entity, Entity):
        return LinkEntity(name=entity.name)
    return entity


class View(ViewInput):
    entity: Annotated[Entity | LinkEntity, BeforeValidator(entity_to_link)] = (
        PydanticField(
            ...,
            description="The entity that this view is associated with.",
        )  # type: ignore[assignment]
    )
    owner: EmailStr = PydanticField(
        ...,
        description="The owner of the view, typically the email of the primary maintainer. This field is required for view creation.",
        title="Owner",
    )

    def get_attributes(self, signals: "Signals", identifiers: list[str] | str):
        """
        Retrieves the online attributes for this view.

        Args:
            signals: The Signals instance to use for retrieving attributes.
            identifiers: The list of entity identifiers to retrieve attributes for.

        Returns:
            The online attributes for the view.
        """

        return signals.get_view_attributes(
            name=self.name,
            version=self.version,
            entity=self.entity.name,
            identifiers=identifiers,
            attributes=[attribute.name for attribute in self.attributes],
        )
