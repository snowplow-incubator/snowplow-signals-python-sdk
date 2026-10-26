import time
import uuid
from datetime import timedelta
from typing import Any, Literal

import pandas as pd

from .api_client import ApiClient
from .attributes_client import AttributesClient
from .dataset_client import DatasetClient
from .interventions_client import InterventionsClient
from .models import (
    AgenticContextResponse,
    AttributeGroup,
    AttributeGroupResponse,
    AttributeKey,
    AttributeKeyId,
    AttributeKeyIdentifiers,
    AttributesWarehouseTable,
    Criteria,
    DatasetBundle,
    DatasetPreviewResponse,
    DatasetRunResponse,
    DatasetRunStatusResponse,
    EventLog,
    EventLogResponse,
    InterventionInstance,
    PredictiveAttribute,
    PredictiveAttributeResponse,
    PredictiveAttributeScore,
    PredictiveAttributeTestResponse,
    PredictiveAttributeTraining,
    RuleIntervention,
    Service,
    SessionAnchors,
    TestAttributeGroupRequest,
    TrainingPreset,
    TrainingRunStatus,
    UserSuppliedAnchors,
    WarehouseTable,
)
from .models.model import (
    AppId,
    DatasetEvent,
)
from .models.model import PredictiveAttribute as PredictiveAttributeDefinition
from .models.model import (
    PredictiveAttributeTrainingRequest,
    TestPredictiveAttributeRequest,
    TrainingSpan,
)
from .predictive_attributes_client import (
    PredictiveAttributesClient,
    PredictiveAttributeTrainingError,
)
from .registry_client import RegistryClient, RegistryObject
from .testing_client import TestingClient


def _exclude_none(**kwargs: Any) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}


def _training_request(
    training_span: TrainingSpan, **options: Any
) -> PredictiveAttributeTrainingRequest:
    return PredictiveAttributeTrainingRequest.model_validate(
        _exclude_none(
            training_data_start=training_span.start_time,
            training_data_end=training_span.end_time,
            **options,
        )
    )


def _training_version(training: PredictiveAttributeTraining | int) -> int:
    if isinstance(training, int):
        return training
    if training.version is None:
        raise ValueError("The training run has no version.")
    return training.version


class BaseSignalsWithApiClient:
    """Internal base class for Signals clients that use an ApiClient"""

    def __init__(
        self,
        *,
        api_client: ApiClient,
    ):
        self.api_client = api_client

        self.interventions = InterventionsClient(api_client=self.api_client)
        self.predictive_attributes = PredictiveAttributesClient(
            api_client=self.api_client
        )
        self.registry = RegistryClient(api_client=self.api_client)
        self.attributes = AttributesClient(api_client=self.api_client)
        self.testing = TestingClient(api_client=self.api_client)
        self.datasets = DatasetClient(api_client=self.api_client)

    def publish(self, objects: list[RegistryObject]) -> list[RegistryObject]:
        """
        Creates or updates the provided objects in the Signals registry and publishes them to the compute engines.
        A predictive attribute that isn't published yet is published with its latest successful
        training. An already published one keeps its live training; use
        publish_predictive_attribute to change it.

        Args:
            objects: The list of objects to publish.
        Returns:
            The list of updated objects
        """
        to_update = [
            object.model_copy(update={"is_published": True}) for object in objects
        ]

        updated_objects = self.registry.create_or_update(objects=to_update)
        return updated_objects

    def unpublish(self, objects: list[RegistryObject]) -> list[RegistryObject]:
        """
        Creates or updates the provided objects in the Signals registry and unpublishes them from the compute engines.

        Args:
            objects: The list of objects to unpublish.
        Returns:
            The list of unpublished objects
        """
        to_update = [
            object.model_copy(update={"is_published": False}) for object in objects
        ]

        updated_objects = self.registry.create_or_update(objects=to_update)
        return updated_objects

    def delete(self, objects: list[RegistryObject]) -> None:
        """
        Deletes the provided objects from the Signals registry.
        Make sure to unpublish the objects first.

        Args:
            objects: The list of objects to delete.
        Returns:
            The list of deleted objects
        """
        self.registry.delete(objects=objects)

    def get_attribute_group(
        self, name: str, version: int | None = None
    ) -> AttributeGroupResponse:
        """
        Returns an Attribute Group from the Signals registry by name.
        If no version is provided, returns the latest one.

        Args:
            name: The name of the Attribute Group.
            version: The version of the Attribute Group.
        Returns:
            The Attribute Group
        """
        attribute_group = self.registry.get_attribute_group(name, version)
        return attribute_group

    def get_group_attributes(
        self,
        name: str,
        version: int,
        attributes: list[str] | str,
        attribute_key: str,
        identifier: str,
    ) -> dict[str, Any]:
        """
        Retrieves the attributes for a given attribute group by name and version.

        Args:
            name: The name of the attribute group.
            version: The version of the attribute group.
            attribute_key: The attribute_key name to retrieve attributes for.
            identifier: The attribute key identifier to retrieve attributes for.
            attributes: The list of attributes to retrieve.
        """
        return self.attributes.get_group_attributes(
            name=name,
            version=version,
            attributes=attributes,
            attribute_key=attribute_key,
            identifier=identifier,
        )

    def get_service_attributes(
        self,
        name: str,
        attribute_key: str,
        identifier: str,
    ) -> dict[str, Any]:
        """
        Retrieves the attributes for a given service by name.

        Args:
            name: The name of the Service.
            attribute_key: The attribute_key to retrieve attributes for.
            identifier: The attribute key identifier to retrieve attributes for.
        """
        return self.attributes.get_service_attributes(
            name=name,
            attribute_key=attribute_key,
            identifier=identifier,
        )

    def get_agentic_context(
        self,
        name: str,
        identifier: str,
        format: Literal["json", "narrative"] = "json",
    ) -> AgenticContextResponse | str:
        """
        Retrieves the agentic context (the buffered events) for a given event
        log by name.

        Args:
            name: The name of the event log.
            identifier: The attribute key value identifying the entity.
            format: The response format. "json" (default) returns a structured
                AgenticContextResponse; "narrative" returns an LLM-ready
                plain-text context block.
        Returns:
            The agentic context for the entity.
        """
        return self.attributes.get_agentic_context(
            name=name,
            identifier=identifier,
            format=format,
        )

    def get_event_log(self, name: str) -> EventLogResponse:
        """
        Returns an Event Log definition from the Signals registry by name.

        Args:
            name: The name of the Event Log.
        Returns:
            The Event Log definition
        """
        return self.registry.get_event_log(name)

    def create_predictive_attribute(
        self, predictive_attribute: PredictiveAttribute
    ) -> PredictiveAttributeResponse:
        """
        Creates a predictive attribute in the Signals registry.
        If the version already exists with the same definition, updates its description and owner.

        Args:
            predictive_attribute: The predictive attribute to create.
        Returns:
            The created predictive attribute.
        """
        return self.predictive_attributes.create(predictive_attribute)

    def train_predictive_attribute(
        self,
        predictive_attribute: PredictiveAttribute | PredictiveAttributeResponse,
        training_span: TrainingSpan,
        preset: TrainingPreset | None = None,
        min_events: int | None = None,
        max_anchors_per_session: int | None = None,
        max_negative_ratio: float | None = None,
        max_lookback_days: int | None = None,
    ) -> PredictiveAttributeTraining:
        """
        Starts training a new model for an existing predictive attribute.
        Training runs asynchronously; use wait_for_predictive_attribute_training to wait for it.

        Args:
            predictive_attribute: The predictive attribute to train.
            training_span: The time span of events to train on.
            preset: "fast" (default) or "thorough" model search.
            min_events: Minimum prior in-session events before an anchor is eligible.
            max_anchors_per_session: Max anchor events to sample per session.
            max_negative_ratio: Max ratio of negative to positive anchors for downsampling.
            max_lookback_days: Override the computed max lookback window (in days).
        Returns:
            The pending training run.
        """
        request = _training_request(
            training_span,
            preset=preset,
            min_events=min_events,
            max_anchors_per_session=max_anchors_per_session,
            max_negative_ratio=max_negative_ratio,
            max_lookback_days=max_lookback_days,
        )
        return self.predictive_attributes.train(predictive_attribute, request)

    def get_predictive_attribute(
        self, name: str, version: int | None = None
    ) -> PredictiveAttributeResponse:
        """
        Returns a predictive attribute, including its trainings, from the Signals registry.
        If no version is provided, returns the latest one.

        Args:
            name: The name of the predictive attribute.
            version: The version of the predictive attribute.
        Returns:
            The predictive attribute
        """
        return self.predictive_attributes.get(name, version)

    def get_predictive_attribute_training(
        self,
        predictive_attribute: PredictiveAttribute | PredictiveAttributeResponse,
        training: PredictiveAttributeTraining | int,
    ) -> PredictiveAttributeTraining:
        """
        Returns the latest state of a training run, including its status and metrics.

        Args:
            predictive_attribute: The predictive attribute the training belongs to.
            training: The training run, or its version.
        Returns:
            The training run
        """
        return self.predictive_attributes.get_training(
            predictive_attribute, _training_version(training)
        )

    def wait_for_predictive_attribute_training(
        self,
        predictive_attribute: PredictiveAttribute | PredictiveAttributeResponse,
        training: PredictiveAttributeTraining | int,
        timeout: timedelta = timedelta(minutes=30),
        poll_interval: timedelta = timedelta(seconds=15),
    ) -> PredictiveAttributeTraining:
        """
        Polls a training run of a predictive attribute until it succeeds.

        Args:
            predictive_attribute: The predictive attribute the training belongs to.
            training: The training run, or its version.
            timeout: How long to wait before giving up.
            poll_interval: How long to wait between status checks.
        Returns:
            The successful training run, including its metrics.
        Raises:
            PredictiveAttributeTrainingError: If the training fails.
            TimeoutError: If the training doesn't finish within the timeout.
        """
        training_version = _training_version(training)
        deadline = time.monotonic() + timeout.total_seconds()
        while True:
            current = self.get_predictive_attribute_training(
                predictive_attribute, training_version
            )
            if current.status == TrainingRunStatus.SUCCESS:
                return current
            if current.status == TrainingRunStatus.FAILED:
                raise PredictiveAttributeTrainingError(
                    f"Training v{training_version} of predictive attribute "
                    f"'{predictive_attribute.name}' failed: {current.error}",
                    training=current,
                )
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Training v{training_version} of predictive attribute "
                    f"'{predictive_attribute.name}' is still {current.status} after {timeout}."
                )
            time.sleep(
                min(
                    poll_interval.total_seconds(),
                    max(0.0, deadline - time.monotonic()),
                )
            )

    def publish_predictive_attribute(
        self,
        predictive_attribute: PredictiveAttribute | PredictiveAttributeResponse,
        training: PredictiveAttributeTraining | int | None = None,
    ) -> None:
        """
        Publishes a training of a predictive attribute to the compute engines so its
        score can be retrieved. Unlike publish([predictive_attribute]), this replaces the
        live training: by default with the latest successful one. Publishing an older
        training rolls back to it. Its input attribute groups must already be published.

        Args:
            predictive_attribute: The predictive attribute to publish.
            training: The training run, or its version. Defaults to the latest successful one.
        """
        current = self.predictive_attributes.get(
            predictive_attribute.name, predictive_attribute.version
        )
        self.predictive_attributes.publish(
            current=current,
            training_version=(
                _training_version(training) if training is not None else None
            ),
        )

    def unpublish_predictive_attribute(
        self,
        predictive_attribute: PredictiveAttribute | PredictiveAttributeResponse,
    ) -> None:
        """
        Unpublishes a predictive attribute from the compute engines.

        Args:
            predictive_attribute: The predictive attribute to unpublish.
        """
        current = self.predictive_attributes.get(
            predictive_attribute.name, predictive_attribute.version
        )
        self.predictive_attributes.unpublish(current=current)

    def get_predictive_attribute_score(
        self, name: str, identifiers: dict[str, str]
    ) -> PredictiveAttributeScore:
        """
        Retrieves the score of a published predictive attribute for an entity.
        Unlike other attributes, a predictive attribute can use attribute groups with
        different attribute keys, so it takes an identifier per attribute key.

        Args:
            name: The name of the predictive attribute.
            identifiers: Mapping of attribute key name to identifier, one for each
                attribute key used by the input attribute groups.
        Returns:
            The predictive attribute score.
        """
        return self.attributes.get_predictive_attribute_score(
            name=name, identifiers=identifiers
        )

    def test(
        self,
        attribute_group: AttributeGroup,
        attribute_key_ids: list[str | AttributeKeyId] | None = None,
        app_ids: list[str] | None = None,
        window: timedelta = timedelta(hours=1),
    ) -> pd.DataFrame:
        """
        Tests the attribute group by extracting the features from the latest window of events in the atomic events table in warehouse.

        Args:
            attribute_group: The attribute group to test.
            attribute_key_ids: The list of attribute key ids (e.g., domain_userid values) to extract features for, as plain strings or AttributeKeyId objects. If empty, random 10 IDs will be used.
            app_ids: The list of app ids to extract features for.
            window: The time window to extract features from.
        """
        request = TestAttributeGroupRequest(
            attribute_group=attribute_group,
            attribute_key_ids=[
                AttributeKeyId(root=k) if isinstance(k, str) else k
                for k in (attribute_key_ids or [])
            ],
            window=window,
            app_ids=[AppId(root=a) for a in (app_ids or [])],
        )
        return self.testing.test_attribute_group(request=request)

    def test_predictive_attribute(
        self,
        predictive_attribute: PredictiveAttribute | PredictiveAttributeResponse,
        training_span: TrainingSpan,
        min_events: int | None = None,
        max_anchors_per_session: int | None = None,
        max_negative_ratio: float | None = None,
    ) -> PredictiveAttributeTestResponse:
        """
        Previews the dataset a training of the predictive attribute would use, without
        creating the predictive attribute or building the dataset. Use it to check there
        is enough data before training.

        Args:
            predictive_attribute: The predictive attribute to test. It doesn't need to exist in the registry.
            training_span: The time span of events to train on.
            min_events: Minimum prior in-session events before an anchor is eligible.
            max_anchors_per_session: Max anchor events to sample per session.
            max_negative_ratio: Max ratio of negative to positive anchors for downsampling.
        Returns:
            The row and session counts, and the training minimums the data misses.
        """
        request = TestPredictiveAttributeRequest(
            # Keeps only the definition, dropping registry fields like trainings
            predictive_attribute=PredictiveAttributeDefinition.model_validate(
                predictive_attribute, from_attributes=True
            ),
            training=_training_request(
                training_span,
                min_events=min_events,
                max_anchors_per_session=max_anchors_per_session,
                max_negative_ratio=max_negative_ratio,
            ),
        )
        return self.testing.test_predictive_attribute(request=request)

    def push_intervention(
        self, targets: AttributeKeyIdentifiers, intervention: InterventionInstance
    ):
        """
        Publish the given intervention to any active subscribers for the given lists of Attribute Keys.

        Args:
            targets: Mapping of Attribute Keys to identifiers to send the intervention to.
            intervention: The intervention payload to publish to the target subscribers.
        Returns:
            Status detailing if the intervention was received by any subscribers.
        """
        return self.interventions.publish(intervention, targets)

    def pull_interventions(self, targets: AttributeKeyIdentifiers):
        """
        Return a subscription for interventions targeting the given Attribute Key targets.

        Args:
            targets: Mapping of Attribute Keys to identifiers to receive interventions for.
        Returns:
            A subscription object that can be started or used as a context manager to receive interventions.
        """
        return self.interventions.subscribe(targets)

    def build_dataset_with_session_anchors(
        self,
        attribute_groups: list[AttributeGroup | AttributeGroupResponse],
        goal_criteria: Criteria,
        training_span: TrainingSpan,
        excluded_events: list[DatasetEvent] | None = None,
        min_events: int | None = None,
        max_anchors_per_session: int | None = None,
        max_negative_ratio: float | None = None,
        anchors_table: WarehouseTable | None = None,
        attributes_table: AttributesWarehouseTable | None = None,
        dataset_table: WarehouseTable | None = None,
        max_lookback_days: int | None = None,
    ) -> DatasetBundle:
        """
        Generate a SQL bundle for building a training dataset using session-based anchors.

        Anchors are automatically derived from sessions matching the goal criteria
        within the training span.

        Args:
            attribute_groups: The attribute groups to include in the dataset.
            goal_criteria: Criteria defining the goal event for anchor generation.
            training_span: The time span to generate anchors from.
            excluded_events: Events to exclude from anchoring (defaults to page_ping).
            min_events: Minimum prior in-session events before an anchor is eligible.
            max_anchors_per_session: Max anchor events to sample per session.
            max_negative_ratio: Max ratio of negative to positive anchors for downsampling.
            anchors_table: Optional output table for the generated anchors.
            attributes_table: Optional table configuration for attribute output tables.
            dataset_table: Optional output table for the assembled dataset.
            max_lookback_days: Override the computed max lookback window (in days).
        Returns:
            A DatasetBundle containing the generated SQL files.
        """
        anchors = SessionAnchors.model_validate(
            _exclude_none(
                goal_criteria=goal_criteria,
                training_span=training_span,
                excluded_events=excluded_events,
                min_events=min_events,
                max_anchors_per_session=max_anchors_per_session,
                max_negative_ratio=max_negative_ratio,
                output=anchors_table,
            )
        )
        return self._build_dataset_sql(
            attribute_groups=attribute_groups,
            anchors=anchors,
            attributes_table=attributes_table,
            dataset_table=dataset_table,
            max_lookback_days=max_lookback_days,
        )

    def build_dataset_with_custom_anchors(
        self,
        attribute_groups: list[AttributeGroup | AttributeGroupResponse],
        anchors_table: WarehouseTable,
        attributes_table: AttributesWarehouseTable | None = None,
        dataset_table: WarehouseTable | None = None,
        max_lookback_days: int | None = None,
    ) -> DatasetBundle:
        """
        Generate a SQL bundle for building a training dataset using user-supplied anchors.

        Anchors are read from a pre-existing warehouse table that the user provides.

        Args:
            attribute_groups: The attribute groups to include in the dataset.
            anchors_table: The warehouse table containing user-supplied anchors.
            attributes_table: Optional table configuration for attribute output tables.
            dataset_table: Optional output table for the assembled dataset.
            max_lookback_days: Override the computed max lookback window (in days).
        Returns:
            A DatasetBundle containing the generated SQL files.
        """
        anchors = UserSuppliedAnchors.model_validate(
            _exclude_none(
                source=anchors_table,
            )
        )
        return self._build_dataset_sql(
            attribute_groups=attribute_groups,
            anchors=anchors,
            attributes_table=attributes_table,
            dataset_table=dataset_table,
            max_lookback_days=max_lookback_days,
        )

    def _build_dataset_sql(
        self,
        attribute_groups: list[AttributeGroup | AttributeGroupResponse],
        anchors: SessionAnchors | UserSuppliedAnchors,
        attributes_table: AttributesWarehouseTable | None = None,
        dataset_table: WarehouseTable | None = None,
        max_lookback_days: int | None = None,
    ) -> DatasetBundle:
        return self.datasets.build_sql(
            attribute_groups=attribute_groups,
            anchors=anchors,
            attributes_database=attributes_table.database if attributes_table else None,
            attributes_schema=attributes_table.schema_ if attributes_table else None,
            attributes_table_prefix=(
                attributes_table.table_prefix if attributes_table else None
            ),
            dataset=dataset_table,
            max_lookback_days=max_lookback_days,
        )

    def submit_dataset_run_with_session_anchors(
        self,
        attribute_groups: list[AttributeGroup | AttributeGroupResponse],
        goal_criteria: Criteria,
        training_span: TrainingSpan,
        excluded_events: list[DatasetEvent] | None = None,
        min_events: int | None = None,
        max_anchors_per_session: int | None = None,
        max_negative_ratio: float | None = None,
        anchors_table: WarehouseTable | None = None,
        attributes_table: AttributesWarehouseTable | None = None,
        dataset_table: WarehouseTable | None = None,
        max_lookback_days: int | None = None,
    ) -> DatasetRunResponse:
        """Submit a dataset build for async execution using session-based anchors.

        Returns immediately with a run ID that can be polled for status.

        Args:
            attribute_groups: The attribute groups to include in the dataset.
            goal_criteria: Criteria defining the goal event for anchor generation.
            training_span: The time span to generate anchors from.
            excluded_events: Events to exclude from anchoring (defaults to page_ping).
            min_events: Minimum prior in-session events before an anchor is eligible.
            max_anchors_per_session: Max anchor events to sample per session.
            max_negative_ratio: Max ratio of negative to positive anchors for downsampling.
            anchors_table: Optional output table for the generated anchors.
            attributes_table: Optional table configuration for attribute output tables.
            dataset_table: Optional output table for the assembled dataset.
            max_lookback_days: Override the computed max lookback window (in days).
        Returns:
            A DatasetRunResponse containing the run ID and dataset table info.
        """
        anchors = SessionAnchors.model_validate(
            _exclude_none(
                goal_criteria=goal_criteria,
                training_span=training_span,
                excluded_events=excluded_events,
                min_events=min_events,
                max_anchors_per_session=max_anchors_per_session,
                max_negative_ratio=max_negative_ratio,
                output=anchors_table,
            )
        )
        return self._submit_dataset_run(
            attribute_groups=attribute_groups,
            anchors=anchors,
            attributes_table=attributes_table,
            dataset_table=dataset_table,
            max_lookback_days=max_lookback_days,
        )

    def submit_dataset_run_with_custom_anchors(
        self,
        attribute_groups: list[AttributeGroup | AttributeGroupResponse],
        anchors_table: WarehouseTable,
        attributes_table: AttributesWarehouseTable | None = None,
        dataset_table: WarehouseTable | None = None,
        max_lookback_days: int | None = None,
    ) -> DatasetRunResponse:
        """Submit a dataset build for async execution using user-supplied anchors.

        Returns immediately with a run ID that can be polled for status.

        Args:
            attribute_groups: The attribute groups to include in the dataset.
            anchors_table: The warehouse table containing user-supplied anchors.
            attributes_table: Optional table configuration for attribute output tables.
            dataset_table: Optional output table for the assembled dataset.
            max_lookback_days: Override the computed max lookback window (in days).
        Returns:
            A DatasetRunResponse containing the run ID and dataset table info.
        """
        anchors = UserSuppliedAnchors.model_validate(
            _exclude_none(
                source=anchors_table,
            )
        )
        return self._submit_dataset_run(
            attribute_groups=attribute_groups,
            anchors=anchors,
            attributes_table=attributes_table,
            dataset_table=dataset_table,
            max_lookback_days=max_lookback_days,
        )

    def get_dataset_run_status(self, run_id: uuid.UUID) -> DatasetRunStatusResponse:
        """Poll the status of an async dataset run.

        Args:
            run_id: The ID of the dataset run to check.
        Returns:
            The current status of the dataset run.
        """
        return self.datasets.get_run_status(run_id)

    def get_dataset_run_preview(
        self, run_id: uuid.UUID, limit: int = 100
    ) -> DatasetPreviewResponse:
        """Fetch a preview of the completed dataset.

        Only available when the run status is SUCCESS.

        Args:
            run_id: The ID of the completed dataset run.
            limit: Maximum number of rows to return (default 100, max 10000).
        Returns:
            A DatasetPreviewResponse with columns, data, and row_count.
        """
        return self.datasets.get_run_preview(run_id, limit)

    def cancel_dataset_run(self, run_id: uuid.UUID) -> None:
        """Cancel a running dataset build.

        Args:
            run_id: The ID of the dataset run to cancel.
        """
        self.datasets.cancel_run(run_id)

    def _submit_dataset_run(
        self,
        attribute_groups: list[AttributeGroup | AttributeGroupResponse],
        anchors: SessionAnchors | UserSuppliedAnchors,
        attributes_table: AttributesWarehouseTable | None = None,
        dataset_table: WarehouseTable | None = None,
        max_lookback_days: int | None = None,
    ) -> DatasetRunResponse:
        return self.datasets.submit_run(
            attribute_groups=attribute_groups,
            anchors=anchors,
            attributes_database=attributes_table.database if attributes_table else None,
            attributes_schema=attributes_table.schema_ if attributes_table else None,
            attributes_table_prefix=(
                attributes_table.table_prefix if attributes_table else None
            ),
            dataset=dataset_table,
            max_lookback_days=max_lookback_days,
        )


class Signals(BaseSignalsWithApiClient):
    """Interface to interact with Snowplow Signals AI"""

    def __init__(
        self,
        *,
        api_url: str,
        api_key: str,
        api_key_id: str,
        org_id: str,
    ):
        super().__init__(
            api_client=ApiClient(
                api_url=api_url,
                api_key=api_key,
                api_key_id=api_key_id,
                org_id=org_id,
                auth_mode="bdp",
            )
        )


class SignalsSandbox(BaseSignalsWithApiClient):
    """Interface to interact with Snowplow Signals AI in SANDBOX mode"""

    def __init__(
        self,
        *,
        api_url: str,
        sandbox_token: str,
    ):
        super().__init__(
            api_client=ApiClient(
                api_url=api_url, auth_mode="sandbox", sandbox_token=sandbox_token
            )
        )
