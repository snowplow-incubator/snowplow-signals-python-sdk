from pydantic import BaseModel

from .api_client import ApiClient, SignalsAPIError
from .models import (
    PredictiveAttribute,
    PredictiveAttributeResponse,
    PredictiveAttributeTraining,
    SelectivePublishRequest,
    TrainingRunStatus,
    UnpublishRequest,
)
from .models.model import (
    PredictiveAttributePublishReference,
    PredictiveAttributeTrainingRequest,
    PredictiveAttributeUnpublishReference,
    PredictiveAttributeUpdate,
)


class PredictiveAttributesClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def create(
        self, predictive_attribute: PredictiveAttribute
    ) -> PredictiveAttributeResponse:
        """
        Creates the predictive attribute. If the version already exists with the
        same definition, updates its description and owner instead.
        """
        try:
            response = self.api_client.make_request(
                method="POST",
                endpoint="registry/predictive_attributes/",
                data=_model_dump(predictive_attribute),
            )
            return PredictiveAttributeResponse.model_validate(response)
        except SignalsAPIError as e:
            if e.status_code != 400:
                raise e

        existing = self.get(predictive_attribute.name, predictive_attribute.version)
        _check_definition_unchanged(predictive_attribute, existing)

        update = PredictiveAttributeUpdate(
            description=predictive_attribute.description,
            owner=predictive_attribute.owner,
        )
        response = self.api_client.make_request(
            method="PUT",
            endpoint=_version_endpoint(
                predictive_attribute.name, predictive_attribute.version
            ),
            data=_model_dump(update),
        )
        return PredictiveAttributeResponse.model_validate(response)

    def get(self, name: str, version: int | None = None) -> PredictiveAttributeResponse:
        endpoint = (
            _version_endpoint(name, version)
            if version is not None
            else f"registry/predictive_attributes/{name}"
        )
        response = self.api_client.make_request(method="GET", endpoint=endpoint)
        return PredictiveAttributeResponse.model_validate(response)

    def delete(
        self, predictive_attribute: PredictiveAttribute | PredictiveAttributeResponse
    ) -> None:
        self.api_client.make_request(
            method="DELETE", endpoint=_endpoint_for(predictive_attribute)
        )

    def train(
        self,
        predictive_attribute: PredictiveAttribute | PredictiveAttributeResponse,
        request: PredictiveAttributeTrainingRequest,
    ) -> PredictiveAttributeTraining:
        response = self.api_client.make_request(
            method="POST",
            endpoint=f"{_endpoint_for(predictive_attribute)}/trainings",
            data=_model_dump(request),
        )
        return PredictiveAttributeTraining.model_validate(response)

    def get_training(
        self,
        predictive_attribute: PredictiveAttribute | PredictiveAttributeResponse,
        training_version: int,
    ) -> PredictiveAttributeTraining:
        response = self.api_client.make_request(
            method="GET",
            endpoint=f"{_endpoint_for(predictive_attribute)}/trainings/{training_version}",
        )
        return PredictiveAttributeTraining.model_validate(response)

    def publish(
        self,
        current: PredictiveAttributeResponse,
        training_version: int | None = None,
    ) -> None:
        """
        Publishes a training of the predictive attribute to the compute engines,
        defaulting to the latest successful one. Does nothing if that training is
        already the published one.
        """
        if training_version is None:
            training_version = _latest_successful_training_version(current)
        if training_version is None:
            raise ValueError(
                f"Predictive attribute '{current.name}' v{current.version} has no successful training to publish. "
                "Train it and wait for the training to succeed before publishing."
            )

        if (
            current.is_published
            and current.published_training_version == training_version
        ):
            return

        request = SelectivePublishRequest(
            predictive_attributes=[
                PredictiveAttributePublishReference(
                    name=current.name,
                    version=_require_version(current),
                    training_version=training_version,
                )
            ]
        )
        self.api_client.make_request(
            method="POST", endpoint="engines/publish", data=_model_dump(request)
        )

    def unpublish(self, current: PredictiveAttributeResponse) -> None:
        """Unpublishes the predictive attribute. Does nothing if it is not published."""
        if not current.is_published:
            return

        request = UnpublishRequest(
            predictive_attributes=[
                PredictiveAttributeUnpublishReference(
                    name=current.name, version=_require_version(current)
                )
            ]
        )
        self.api_client.make_request(
            method="POST", endpoint="engines/unpublish", data=_model_dump(request)
        )


def _require_version(
    predictive_attribute: PredictiveAttribute | PredictiveAttributeResponse,
) -> int:
    if predictive_attribute.version is None:
        raise ValueError(
            f"Predictive attribute '{predictive_attribute.name}' has no version."
        )
    return predictive_attribute.version


def _endpoint_for(
    predictive_attribute: PredictiveAttribute | PredictiveAttributeResponse,
) -> str:
    return _version_endpoint(
        predictive_attribute.name, _require_version(predictive_attribute)
    )


def _version_endpoint(name: str, version: int) -> str:
    return f"registry/predictive_attributes/{name}/versions/{version}"


def _latest_successful_training_version(
    current: PredictiveAttributeResponse,
) -> int | None:
    successful = [
        training.version
        for training in current.trainings or []
        if training.version is not None and training.status == TrainingRunStatus.SUCCESS
    ]
    return max(successful, default=None)


def _check_definition_unchanged(
    predictive_attribute: PredictiveAttribute, existing: PredictiveAttributeResponse
) -> None:
    def input_keys(model: PredictiveAttribute | PredictiveAttributeResponse):
        return {
            (ref.name, ref.version, ref.attribute_name)
            for ref in model.input_attributes
        }

    def goal(criteria: BaseModel) -> dict:
        return criteria.model_dump(mode="json", exclude_none=True)

    def excluded(model: PredictiveAttribute | PredictiveAttributeResponse):
        return {event.name for event in model.excluded_events or []}

    if (
        input_keys(predictive_attribute) != input_keys(existing)
        or goal(predictive_attribute.goal_criteria) != goal(existing.goal_criteria)
        or excluded(predictive_attribute) != excluded(existing)
    ):
        raise ValueError(
            f"Predictive attribute '{predictive_attribute.name}' v{predictive_attribute.version} "
            "already exists with different input attributes, goal criteria or excluded events. "
            "Only description and owner can be changed; bump the version to change the definition."
        )


def _model_dump(model: BaseModel) -> dict:
    return model.model_dump(mode="json", exclude_none=True, by_alias=True)
