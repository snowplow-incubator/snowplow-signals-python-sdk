from typing import TYPE_CHECKING, Annotated, Any, List, Optional

from pydantic import BaseModel, BeforeValidator, Field, model_validator

from .attribute_key import AttributeKey
from .event_log import EventLog, attribute_key_to_link
from .model import AgenticAttribute as AgenticAttributeInput
from .model import (
    AgenticAttributeResult,
    CriteriaAllInput,
    CriteriaAnyInput,
    CriteriaNoneInput,
    CriteriaTriggerInput,
    LinkAttributeKey,
    SignalsApiModelsInterventionCriterionCriterion,
)

if TYPE_CHECKING:
    from snowplow_signals.signals import Signals


def _context_names(contexts: Any) -> Any:
    if isinstance(contexts, list):
        return [
            context.name if isinstance(context, EventLog) else context
            for context in contexts
        ]
    return contexts


def _to_trigger(trigger: Any) -> Any:
    if isinstance(trigger, CriteriaTriggerInput):
        return trigger
    # A trigger serialized from the API has its criteria under "criteria"
    if isinstance(trigger, dict) and "criteria" in trigger:
        return trigger
    # Anything else is a criterion or group of criteria, which is all a criteria
    # trigger holds
    if isinstance(trigger, (BaseModel, dict)):
        return CriteriaTriggerInput(criteria=trigger)
    return trigger


def _wrap_triggers(triggers: Any) -> Any:
    if isinstance(triggers, list):
        return [_to_trigger(trigger) for trigger in triggers]
    return triggers


class AgenticAttribute(AgenticAttributeInput):
    """
    An agentic attribute is evaluated by an LLM. When one of its triggers fires,
    the model reviews the configured agentic contexts (event logs) and writes its
    answer to the profile under the given attribute key.
    """

    attribute_key: Annotated[
        AttributeKey | LinkAttributeKey,
        BeforeValidator(attribute_key_to_link),
    ] = Field(  # type: ignore[assignment]
        ...,
        description="The attribute key the agentic attribute is written under. Must be 'domain_sessionid'.",
    )
    contexts: Annotated[
        List[str | EventLog],
        BeforeValidator(_context_names),
    ] = Field(  # type: ignore[assignment]
        ...,
        description="The published agentic contexts (event logs) the model reviews, as event logs or event log names.",
        max_length=5,
        min_length=1,
        title="Contexts",
    )
    triggers: Annotated[
        List[
            CriteriaTriggerInput
            | CriteriaAllInput
            | CriteriaAnyInput
            | CriteriaNoneInput
            | SignalsApiModelsInterventionCriterionCriterion
        ],
        BeforeValidator(_wrap_triggers),
    ] = Field(  # type: ignore[assignment]
        ...,
        description="When the attribute is evaluated: whenever any of the triggers holds. Each trigger is a criterion or group of criteria, optionally wrapped in a CriteriaTrigger.",
        max_length=5,
        min_length=1,
        title="Triggers",
    )
    is_published: Optional[bool] = Field(
        default=False,
        description="Whether this agentic attribute has been published to the compute engines.",
        title="Is Published",
    )

    @model_validator(mode="after")
    def _check_values_match_output_type(self) -> "AgenticAttribute":
        if self.output_type == "enum" and not self.values:
            raise ValueError("values are required when output_type is 'enum'.")
        if self.output_type != "enum" and self.values:
            raise ValueError(
                f"values can only be set when output_type is 'enum', not '{self.output_type}'."
            )
        return self

    def get_value(self, signals: "Signals", identifier: str) -> AgenticAttributeResult:
        """
        Retrieves the most recently evaluated value of this agentic attribute.

        Args:
            signals: The Signals instance to use for retrieving the value.
            identifier: The attribute key identifier (e.g. the domain_sessionid).

        Returns:
            The latest value, with the model's justification.
        """
        return signals.get_agentic_attribute_value(
            name=self.name,
            identifier=identifier,
        )
