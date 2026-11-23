import os
import sys
import warnings
from typing import Any

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


class PredictiveAttributeTrainingError(Exception):
    """Raised when a training run of a predictive attribute fails."""

    def __init__(self, message: str, training: PredictiveAttributeTraining):
        super().__init__(message)
        self.training = training


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
            # A 400 can also be a validation error, so only treat it as
            # "already exists" if the version can be fetched
            existing = self.get_if_exists(
                predictive_attribute.name, predictive_attribute.version
            )
            if existing is None:
                raise e

        check_definition_unchanged(predictive_attribute, existing)

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

    def get_if_exists(
        self, name: str, version: int | None = None
    ) -> PredictiveAttributeResponse | None:
        try:
            return self.get(name, version)
        except SignalsAPIError as e:
            if e.status_code == 404:
                return None
            raise e

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
            raise _no_successful_training_error(current)

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


def check_publishable(
    predictive_attribute: PredictiveAttribute,
    current: PredictiveAttributeResponse | None,
) -> None:
    """
    Raises if publishing the predictive attribute would fail because it is not
    published yet and has no successful training.
    """
    if current is not None and (
        current.is_published or _latest_successful_training_version(current) is not None
    ):
        return
    raise _no_successful_training_error(predictive_attribute)


def warn_if_newer_training(current: PredictiveAttributeResponse) -> None:
    latest = _latest_successful_training_version(current)
    published = current.published_training_version
    if not current.is_published or latest is None or published is None:
        return
    if latest > published:
        warnings.warn(
            f"Predictive attribute '{current.name}' v{current.version} is live with training "
            f"v{published}, but training v{latest} is newer. Use "
            "Signals.publish_predictive_attribute to publish it.",
            stacklevel=_caller_stacklevel(),
        )


_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))


def _caller_stacklevel() -> int:
    """The stacklevel of the first frame outside this package, for warnings.warn
    called from the function that calls this."""
    stacklevel = 1
    frame = sys._getframe(1)
    while frame.f_back is not None and frame.f_code.co_filename.startswith(
        _PACKAGE_DIR
    ):
        frame = frame.f_back
        stacklevel += 1
    return stacklevel


def _no_successful_training_error(
    predictive_attribute: PredictiveAttribute | PredictiveAttributeResponse,
) -> ValueError:
    return ValueError(
        f"Predictive attribute '{predictive_attribute.name}' v{predictive_attribute.version} "
        "has no successful training to publish. "
        "Train it and wait for the training to succeed before publishing."
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


def check_definition_unchanged(
    predictive_attribute: PredictiveAttribute, existing: PredictiveAttributeResponse
) -> None:
    """
    Raises if the predictive attribute differs from the registered version in
    anything other than description and owner.
    """
    if (
        _input_keys(predictive_attribute) != _input_keys(existing)
        or _goal(predictive_attribute) != _goal(existing)
        or _excluded_event_names(predictive_attribute)
        != _excluded_event_names(existing)
    ):
        raise ValueError(
            f"Predictive attribute '{predictive_attribute.name}' v{predictive_attribute.version} "
            "already exists with different input attributes, goal criteria or excluded events. "
            "Only description and owner can be changed; bump the version to change the definition."
        )


def _input_keys(
    predictive_attribute: PredictiveAttribute | PredictiveAttributeResponse,
) -> set[tuple[str, int, str]]:
    return {
        (ref.name, ref.version, ref.attribute_name)
        for ref in predictive_attribute.input_attributes
    }


def _goal(
    predictive_attribute: PredictiveAttribute | PredictiveAttributeResponse,
) -> dict[str, Any]:
    return predictive_attribute.goal_criteria.model_dump(mode="json", exclude_none=True)


def _excluded_event_names(
    predictive_attribute: PredictiveAttribute | PredictiveAttributeResponse,
) -> set[str]:
    return {event.name for event in predictive_attribute.excluded_events or []}


def _model_dump(model: BaseModel) -> dict:
    return model.model_dump(mode="json", exclude_none=True, by_alias=True)
