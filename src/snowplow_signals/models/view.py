from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import BeforeValidator, EmailStr
from pydantic import Field
from pydantic import Field as PydanticField

from .model import (
    AttributeInput,
    BatchSource,
    Entity,
    FieldModel,
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

    def get_attributes(self, signals: "Signals", identifier: str):
        """
        Retrieves the attributes for this view.

        Args:
            signals: The Signals instance to use for retrieving attributes.
            identifier: The entity identifier to retrieve attributes for.

        Returns:
            The attributes for the view.
        """

        return signals.get_view_attributes(
            name=self.name,
            version=self.version,
            entity=self.entity.name,
            identifier=identifier,
            attributes=[attribute.name for attribute in self.attributes],
        )


class StreamOrBatchView(View):
    fields: Literal[None] = Field(
        default=None,
        description="Not applicable.",
    )
    attributes: list[AttributeInput] = Field(
        description="The list of attributes that will be calculated from events as part of this view.",
        title="Attributes",
        min_length=1,
    )


class StreamView(StreamOrBatchView):
    """
    A stream view is a view that is calculated from events in real-time using the Signals streaming engine.
    """

    offline: Literal[False] = Field(
        default=False,
        description="A boolean indicating whether the attributes are pre-computed in the warehouse.",
        title="Offline",
    )
    batch_source: Literal[None] = Field(
        default=None,
        description="Not applicable for stream views.",
        title="Batch Source",
    )


class BatchView(StreamOrBatchView):
    """
    A batch view is a view that is calculated from events in batch using the Signals batch engine.
    """

    offline: Literal[True] = Field(
        default=True,
        description="A boolean indicating whether the attributes are pre-computed in the warehouse.",
        title="Offline",
    )


class ExternalBatchView(View):
    """
    An external batch view is a view that is derived from an existing warehouse table.
    """

    offline: Literal[True] = Field(
        default=True,
        description="A boolean indicating whether the attributes are pre-computed in the warehouse.",
        title="Offline",
    )
    fields: list[FieldModel] = Field(
        description="The list of table columns that are part of this view during materialization.",
        title="Fields",
        min_length=1,
    )
    attributes: Literal[None] = Field(
        default=None,
        description="Not applicable for warehouse table views.",
        title="Attributes",
    )
    batch_source: BatchSource = Field(
        description="The batch source for materializing this view from the warehouse.",
        title="Batch Source",
    )
