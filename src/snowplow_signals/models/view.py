from pydantic import Field as PydanticField, BeforeValidator, EmailStr
from typing import Annotated
from .model import (
    ViewInput,
    Entity,
    LinkEntity,
)


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
