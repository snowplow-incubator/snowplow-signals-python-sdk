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
    Anchors,
    AttributeGroup,
    AttributeGroupResponse,
    AttributeKey,
    AttributeKeyId,
    AttributeKeyIdentifiers,
    AttributesWarehouseTable,
    Criteria,
    DatasetBundle,
    DatasetOutcome,
    DatasetPreviewResponse,
    DatasetRunResponse,
    DatasetRunStatusResponse,
    EventAnchors,
    EventLog,
    EventLogResponse,
    InterventionInstance,
    RuleIntervention,
    Service,
    SessionAnchors,
    SessionSample,
    TestAttributeGroupRequest,
    TriggerAnchors,
    UserSuppliedAnchors,
    WarehouseTable,
)
from .models.model import (
    AgenticAttributeEvaluationPolicy,
)
from .models.model import CriteriaTriggerInput as CriteriaTrigger
from .models.model import (
    DatasetEvent,
    TrainingSpan,
)
from .registry_client import RegistryClient, RegistryObject
from .testing_client import TestingClient


def _exclude_none(**kwargs: Any) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}


class BaseSignalsWithApiClient:
    """Internal base class for Signals clients that use an ApiClient"""

    def __init__(
        self,
        *,
        api_client: ApiClient,
    ):
        self.api_client = api_client

        self.interventions = InterventionsClient(api_client=self.api_client)
        self.registry = RegistryClient(api_client=self.api_client)
        self.attributes = AttributesClient(api_client=self.api_client)
        self.testing = TestingClient(api_client=self.api_client)
        self.datasets = DatasetClient(api_client=self.api_client)

    def publish(self, objects: list[RegistryObject]) -> list[RegistryObject]:
        """
        Creates or updates the provided objects in the Signals registry and publishes them to the compute engines.

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

    def test(
        self,
        attribute_group: AttributeGroup,
        attribute_key_ids: list[AttributeKeyId] = [],
        app_ids: list[str] = [],
        window: timedelta = timedelta(hours=1),
    ) -> pd.DataFrame:
        """
        Tests the attribute group by extracting the features from the latest window of events in the atomic events table in warehouse.

        Args:
            attribute_group: The attribute group to test.
            attribute_key_ids: The list of attribute key ids (e.g., domain_userid values) to extract features for. If empty, random 10 IDs will be used.
            app_ids: The list of app ids to extract features for.
            window: The time window to extract features from.
        """
        request = TestAttributeGroupRequest(
            attribute_group=attribute_group,
            attribute_key_ids=attribute_key_ids,
            window=window,
            app_ids=app_ids,  # pyright: ignore[reportArgumentType] AppID is already a string, validation happens at runtime
        )
        return self.testing.test_attribute_group(request=request)

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
        outcomes: list[DatasetOutcome] | None = None,
        event_logs: list[EventLog | EventLogResponse] | None = None,
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
            outcomes: Outcome columns: whether matching events happened after each anchor.
            event_logs: Event logs to add as columns, as buffered at each anchor (Snowflake only).
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
            outcomes=outcomes,
            event_logs=event_logs,
        )

    def build_dataset_with_custom_anchors(
        self,
        attribute_groups: list[AttributeGroup | AttributeGroupResponse],
        anchors_table: WarehouseTable,
        attributes_table: AttributesWarehouseTable | None = None,
        dataset_table: WarehouseTable | None = None,
        max_lookback_days: int | None = None,
        outcomes: list[DatasetOutcome] | None = None,
        event_logs: list[EventLog | EventLogResponse] | None = None,
        has_label: bool | None = None,
    ) -> DatasetBundle:
        """
        Generate a SQL bundle for building a training dataset using user-supplied anchors.

        Anchors are read from a pre-existing warehouse table that the user provides.

        Args:
            attribute_groups: The attribute groups to include in the dataset.
            anchors_table: The warehouse table containing user-supplied anchors.
            has_label: Whether the table has a `label` column (default True). Set False for tables of moments without labels, such as logs of past model calls.
            attributes_table: Optional table configuration for attribute output tables.
            dataset_table: Optional output table for the assembled dataset.
            max_lookback_days: Override the computed max lookback window (in days).
            outcomes: Outcome columns: whether matching events happened after each anchor.
            event_logs: Event logs to add as columns, as buffered at each anchor (Snowflake only).
        Returns:
            A DatasetBundle containing the generated SQL files.
        """
        anchors = UserSuppliedAnchors.model_validate(
            _exclude_none(
                source=anchors_table,
                has_label=has_label,
            )
        )
        return self._build_dataset_sql(
            attribute_groups=attribute_groups,
            anchors=anchors,
            attributes_table=attributes_table,
            dataset_table=dataset_table,
            max_lookback_days=max_lookback_days,
            outcomes=outcomes,
            event_logs=event_logs,
        )

    def _build_dataset_sql(
        self,
        attribute_groups: list[AttributeGroup | AttributeGroupResponse],
        anchors: Anchors,
        attributes_table: AttributesWarehouseTable | None = None,
        dataset_table: WarehouseTable | None = None,
        max_lookback_days: int | None = None,
        outcomes: list[DatasetOutcome] | None = None,
        event_logs: list[EventLog | EventLogResponse] | None = None,
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
            outcomes=outcomes,
            event_logs=event_logs,
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
        outcomes: list[DatasetOutcome] | None = None,
        event_logs: list[EventLog | EventLogResponse] | None = None,
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
            outcomes: Outcome columns: whether matching events happened after each anchor.
            event_logs: Event logs to add as columns, as buffered at each anchor (Snowflake only).
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
            outcomes=outcomes,
            event_logs=event_logs,
        )

    def submit_dataset_run_with_custom_anchors(
        self,
        attribute_groups: list[AttributeGroup | AttributeGroupResponse],
        anchors_table: WarehouseTable,
        attributes_table: AttributesWarehouseTable | None = None,
        dataset_table: WarehouseTable | None = None,
        max_lookback_days: int | None = None,
        outcomes: list[DatasetOutcome] | None = None,
        event_logs: list[EventLog | EventLogResponse] | None = None,
        has_label: bool | None = None,
    ) -> DatasetRunResponse:
        """Submit a dataset build for async execution using user-supplied anchors.

        Returns immediately with a run ID that can be polled for status.

        Args:
            attribute_groups: The attribute groups to include in the dataset.
            anchors_table: The warehouse table containing user-supplied anchors.
            has_label: Whether the table has a `label` column (default True). Set False for tables of moments without labels, such as logs of past model calls.
            attributes_table: Optional table configuration for attribute output tables.
            dataset_table: Optional output table for the assembled dataset.
            max_lookback_days: Override the computed max lookback window (in days).
            outcomes: Outcome columns: whether matching events happened after each anchor.
            event_logs: Event logs to add as columns, as buffered at each anchor (Snowflake only).
        Returns:
            A DatasetRunResponse containing the run ID and dataset table info.
        """
        anchors = UserSuppliedAnchors.model_validate(
            _exclude_none(
                source=anchors_table,
                has_label=has_label,
            )
        )
        return self._submit_dataset_run(
            attribute_groups=attribute_groups,
            anchors=anchors,
            attributes_table=attributes_table,
            dataset_table=dataset_table,
            max_lookback_days=max_lookback_days,
            outcomes=outcomes,
            event_logs=event_logs,
        )

    def build_dataset_with_event_anchors(
        self,
        attribute_groups: list[AttributeGroup | AttributeGroupResponse],
        criteria: Criteria,
        training_span: TrainingSpan,
        max_per_session: int | None = None,
        pick: Literal["first", "random"] | None = None,
        seed: str | None = None,
        include_anchor_event: bool | None = None,
        sample: SessionSample | None = None,
        anchors_table: WarehouseTable | None = None,
        attributes_table: AttributesWarehouseTable | None = None,
        dataset_table: WarehouseTable | None = None,
        max_lookback_days: int | None = None,
        outcomes: list[DatasetOutcome] | None = None,
        event_logs: list[EventLog | EventLogResponse] | None = None,
    ) -> DatasetBundle:
        """
        Generate a SQL bundle for a dataset with one anchor per matching event.

        Use it for the moments an application calls a model in response to an event,
        such as a product page view.

        Args:
            attribute_groups: The attribute groups to include in the dataset.
            criteria: Events to anchor on.
            training_span: The time span to generate anchors from.
            max_per_session: Maximum anchors per session (default: every matching event).
            pick: Which events to keep above max_per_session: "first" or "random".
            seed: Seed for the random pick.
            include_anchor_event: Whether attributes and event logs include the anchor event.
            sample: Use only a deterministic sample of sessions.
            anchors_table: Optional output table for the generated anchors.
            attributes_table: Optional table configuration for attribute output tables.
            dataset_table: Optional output table for the assembled dataset.
            max_lookback_days: Override the computed max lookback window (in days).
            outcomes: Outcome columns: whether matching events happened after each anchor.
            event_logs: Event logs to add as columns, as buffered at each anchor (Snowflake only).
        Returns:
            A DatasetBundle containing the generated SQL files.
        """
        return self._build_dataset_sql(
            attribute_groups=attribute_groups,
            anchors=self._event_anchors(
                criteria,
                training_span,
                max_per_session,
                pick,
                seed,
                include_anchor_event,
                sample,
                anchors_table,
            ),
            attributes_table=attributes_table,
            dataset_table=dataset_table,
            max_lookback_days=max_lookback_days,
            outcomes=outcomes,
            event_logs=event_logs,
        )

    def submit_dataset_run_with_event_anchors(
        self,
        attribute_groups: list[AttributeGroup | AttributeGroupResponse],
        criteria: Criteria,
        training_span: TrainingSpan,
        max_per_session: int | None = None,
        pick: Literal["first", "random"] | None = None,
        seed: str | None = None,
        include_anchor_event: bool | None = None,
        sample: SessionSample | None = None,
        anchors_table: WarehouseTable | None = None,
        attributes_table: AttributesWarehouseTable | None = None,
        dataset_table: WarehouseTable | None = None,
        max_lookback_days: int | None = None,
        outcomes: list[DatasetOutcome] | None = None,
        event_logs: list[EventLog | EventLogResponse] | None = None,
    ) -> DatasetRunResponse:
        """Submit a dataset build with one anchor per matching event for async execution.

        Takes the same arguments as `build_dataset_with_event_anchors`.

        Returns:
            A DatasetRunResponse containing the run ID and dataset table info.
        """
        return self._submit_dataset_run(
            attribute_groups=attribute_groups,
            anchors=self._event_anchors(
                criteria,
                training_span,
                max_per_session,
                pick,
                seed,
                include_anchor_event,
                sample,
                anchors_table,
            ),
            attributes_table=attributes_table,
            dataset_table=dataset_table,
            max_lookback_days=max_lookback_days,
            outcomes=outcomes,
            event_logs=event_logs,
        )

    def build_dataset_with_trigger_anchors(
        self,
        attribute_groups: list[AttributeGroup | AttributeGroupResponse],
        triggers: list[CriteriaTrigger],
        training_span: TrainingSpan,
        evaluation_policy: AgenticAttributeEvaluationPolicy | None = None,
        sample: SessionSample | None = None,
        anchors_table: WarehouseTable | None = None,
        attributes_table: AttributesWarehouseTable | None = None,
        dataset_table: WarehouseTable | None = None,
        max_lookback_days: int | None = None,
        outcomes: list[DatasetOutcome] | None = None,
        event_logs: list[EventLog | EventLogResponse] | None = None,
    ) -> DatasetBundle:
        """
        Generate a SQL bundle for a dataset anchored where an agentic attribute would have fired.

        The triggers and evaluation policy take the same shape as on an agentic attribute.
        Attributes in the dataset include the triggering event.

        Args:
            attribute_groups: The attribute groups to include. Must contain the attributes the triggers reference.
            triggers: Criteria triggers, as on an agentic attribute.
            training_span: The time span to replay.
            evaluation_policy: Cooldown and per-session cap, as on an agentic attribute.
            sample: Replay only a deterministic sample of sessions.
            anchors_table: Optional output table for the generated anchors.
            attributes_table: Optional table configuration for attribute output tables.
            dataset_table: Optional output table for the assembled dataset.
            max_lookback_days: Override the computed max lookback window (in days).
            outcomes: Outcome columns: whether matching events happened after each anchor.
            event_logs: Event logs to add as columns, as buffered at each anchor (Snowflake only).
        Returns:
            A DatasetBundle containing the generated SQL files.
        """
        return self._build_dataset_sql(
            attribute_groups=attribute_groups,
            anchors=self._trigger_anchors(
                triggers, training_span, evaluation_policy, sample, anchors_table
            ),
            attributes_table=attributes_table,
            dataset_table=dataset_table,
            max_lookback_days=max_lookback_days,
            outcomes=outcomes,
            event_logs=event_logs,
        )

    def submit_dataset_run_with_trigger_anchors(
        self,
        attribute_groups: list[AttributeGroup | AttributeGroupResponse],
        triggers: list[CriteriaTrigger],
        training_span: TrainingSpan,
        evaluation_policy: AgenticAttributeEvaluationPolicy | None = None,
        sample: SessionSample | None = None,
        anchors_table: WarehouseTable | None = None,
        attributes_table: AttributesWarehouseTable | None = None,
        dataset_table: WarehouseTable | None = None,
        max_lookback_days: int | None = None,
        outcomes: list[DatasetOutcome] | None = None,
        event_logs: list[EventLog | EventLogResponse] | None = None,
    ) -> DatasetRunResponse:
        """Submit a dataset build anchored where an agentic attribute would have fired.

        Takes the same arguments as `build_dataset_with_trigger_anchors`.

        Returns:
            A DatasetRunResponse containing the run ID and dataset table info.
        """
        return self._submit_dataset_run(
            attribute_groups=attribute_groups,
            anchors=self._trigger_anchors(
                triggers, training_span, evaluation_policy, sample, anchors_table
            ),
            attributes_table=attributes_table,
            dataset_table=dataset_table,
            max_lookback_days=max_lookback_days,
            outcomes=outcomes,
            event_logs=event_logs,
        )

    @staticmethod
    def _event_anchors(
        criteria: Criteria,
        training_span: TrainingSpan,
        max_per_session: int | None,
        pick: Literal["first", "random"] | None,
        seed: str | None,
        include_anchor_event: bool | None,
        sample: SessionSample | None,
        anchors_table: WarehouseTable | None,
    ) -> EventAnchors:
        return EventAnchors.model_validate(
            _exclude_none(
                criteria=criteria,
                training_span=training_span,
                max_per_session=max_per_session,
                pick=pick,
                seed=seed,
                include_anchor_event=include_anchor_event,
                sample=sample,
                output=anchors_table,
            )
        )

    @staticmethod
    def _trigger_anchors(
        triggers: list[CriteriaTrigger],
        training_span: TrainingSpan,
        evaluation_policy: AgenticAttributeEvaluationPolicy | None,
        sample: SessionSample | None,
        anchors_table: WarehouseTable | None,
    ) -> TriggerAnchors:
        return TriggerAnchors.model_validate(
            _exclude_none(
                triggers=triggers,
                training_span=training_span,
                evaluation_policy=evaluation_policy,
                sample=sample,
                output=anchors_table,
            )
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
        anchors: Anchors,
        attributes_table: AttributesWarehouseTable | None = None,
        dataset_table: WarehouseTable | None = None,
        max_lookback_days: int | None = None,
        outcomes: list[DatasetOutcome] | None = None,
        event_logs: list[EventLog | EventLogResponse] | None = None,
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
            outcomes=outcomes,
            event_logs=event_logs,
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
