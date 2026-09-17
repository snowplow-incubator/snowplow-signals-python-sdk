from typing import TYPE_CHECKING, Annotated, List, Literal, Optional

from pydantic import BeforeValidator, Field

from .attribute_key import AttributeKey
from .model import EventLog as EventLogInput
from .model import EventSelection as EventSelectionInput
from .model import LinkAttributeKey
from .property_wrapper import _EventLogProperty

if TYPE_CHECKING:
    from snowplow_signals.signals import Signals


def attribute_key_to_link(
    attribute_key: AttributeKey | LinkAttributeKey,
) -> LinkAttributeKey:
    if isinstance(attribute_key, AttributeKey):
        return LinkAttributeKey(name=attribute_key.name)
    return attribute_key


class EventSelection(EventSelectionInput):
    """One event schema to project properties from, within an event log."""

    properties: List[_EventLogProperty] = Field(  # type: ignore[assignment]
        ...,
        description="Properties to project from each matching event.",
        max_length=50,
        min_length=1,
    )


class EventLog(EventLogInput):
    """
    An event log buffers a window of recent events for an attribute key, ready to
    be read back as an LLM-friendly context block.
    """

    attribute_key: Annotated[
        AttributeKey | LinkAttributeKey,
        BeforeValidator(attribute_key_to_link),
    ] = Field(
        ...,
        description="Reference to the attribute key this event log is scoped to. For v1 the attribute key name must be 'domain_sessionid'.",
    )
    events: List[EventSelection] = Field(  # type: ignore[assignment]
        ...,
        description="The events to log and, for each, the properties to project.",
        max_length=20,
        min_length=1,
    )
    is_published: Optional[bool] = Field(
        default=False,
        description="Whether this event log has been published to the compute engines.",
        title="Is Published",
    )

    def get_agentic_context(
        self,
        signals: "Signals",
        identifier: str,
        format: Literal["json", "narrative"] = "json",
    ):
        """
        Retrieves the agentic context (the buffered events) for this event log.

        Args:
            signals: The Signals instance to use for retrieving the context.
            identifier: The attribute key identifier to retrieve the context for.
            format: The response format. "json" (default) returns a structured
                AgenticContextResponse; "narrative" returns an LLM-ready
                plain-text context block.

        Returns:
            The agentic context for the entity.
        """

        return signals.get_agentic_context(
            name=self.name,
            identifier=identifier,
            format=format,
        )
