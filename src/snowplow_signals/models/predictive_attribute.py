from enum import StrEnum
from typing import TYPE_CHECKING, Literal

from pydantic import EmailStr, Field

from .criteria_wrapper import Criteria
from .model import DatasetEvent
from .model import PredictiveAttribute as PredictiveAttributeInput
from .model import PredictiveAttributeResponse as PredictiveAttributeResponseModel
from .model import PredictiveAttributeScore
from .model import PredictiveAttributeTraining as PredictiveAttributeTrainingModel
from .model import SourceGroupReference

if TYPE_CHECKING:
    from snowplow_signals.signals import Signals


class TrainingRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class PredictiveAttributeTraining(PredictiveAttributeTrainingModel):
    """A training run of a predictive attribute's model."""

    status: TrainingRunStatus = Field(  # type: ignore[assignment]
        default=TrainingRunStatus.PENDING,
        description="The status of the training run.",
        title="Status",
    )
    preset: Literal["fast", "thorough"] = Field(  # type: ignore[assignment]
        default="fast",
        description="The model search preset used for training.",
        title="Preset",
    )


class PredictiveAttributeResponse(PredictiveAttributeResponseModel):
    """A predictive attribute as stored in the Signals registry, with its training runs."""

    trainings: list[PredictiveAttributeTraining] = Field(  # type: ignore[assignment]
        default_factory=list,
        description="The training runs of this predictive attribute, ordered by version.",
        title="Trainings",
    )


class PredictiveAttribute(PredictiveAttributeInput):
    """
    A predictive attribute is a score produced by an ML model trained on the
    attributes of other attribute groups.

    Once published, its score is computed in real time from the latest values of the
    input attributes and retrieved with `Signals.get_predictive_attribute_score`.
    """

    version: int = Field(  # type: ignore[assignment]
        default=1,
        ge=1,
        description="The version of the predictive attribute. Bump it to change input attributes, goal criteria or excluded events.",
        title="Version",
    )

    input_attributes: list[SourceGroupReference] = Field(  # type: ignore[assignment]
        ...,
        description="The attributes used as model inputs, from stream attribute groups. Use `attribute_group.attribute_reference(name)` to build them.",
        min_length=1,
        title="Input Attributes",
    )
    goal_criteria: Criteria = Field(  # type: ignore[assignment]
        ...,
        description="Criteria defining the goal event the model predicts.",
        title="Goal Criteria",
    )
    excluded_events: list[DatasetEvent] = Field(  # type: ignore[assignment]
        default_factory=lambda: [DatasetEvent(name="page_ping")],
        description="Events to exclude from anchoring during training.",
        title="Excluded Events",
    )
    owner: EmailStr = Field(  # type: ignore[assignment]
        ...,
        description="The owner of the predictive attribute, typically the email of the primary maintainer. This field is required for predictive attribute creation.",
        title="Owner",
    )
    is_published: bool = Field(
        default=False,
        exclude=True,
        description="Client-side control for whether to publish the latest successful training to the compute engines.",
        title="Is Published",
    )

    def get_score(
        self, signals: "Signals", identifiers: dict[str, str]
    ) -> PredictiveAttributeScore:
        """
        Retrieves the score of this predictive attribute for an entity.

        Args:
            signals: The Signals instance to use for retrieving the score.
            identifiers: Mapping of attribute key name to identifier, one for each
                attribute key used by the input attribute groups.

        Returns:
            The predictive attribute score.
        """
        return signals.get_predictive_attribute_score(
            name=self.name, identifiers=identifiers
        )
