from pydantic import BaseModel

from .api_client import ApiClient, SignalsAPIError
from .models import (
    AttributeGroup,
    AttributeGroupResponse,
    AttributeKey,
    EventLog,
    EventLogReference,
    EventLogResponse,
    PredictiveAttribute,
    PredictiveAttributeResponse,
    RuleIntervention,
    SelectivePublishRequest,
    Service,
    UnpublishRequest,
)
from .predictive_attributes_client import (
    PredictiveAttributesClient,
    check_definition_unchanged,
    check_publishable,
    warn_if_newer_training,
)

RegistryObject = (
    AttributeGroup
    | Service
    | AttributeKey
    | RuleIntervention
    | EventLog
    | PredictiveAttribute
)


class RegistryClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client
        self.predictive_attributes = PredictiveAttributesClient(api_client=api_client)

    def create_or_update(self, objects: list[RegistryObject]) -> list[RegistryObject]:
        updated_objects: list[RegistryObject] = []

        # Check predictive attributes before changing anything
        registered: list[
            tuple[PredictiveAttribute, PredictiveAttributeResponse | None]
        ] = []
        for object in objects:
            if isinstance(object, PredictiveAttribute):
                current = self.predictive_attributes.get_if_exists(
                    object.name, object.version
                )
                if current is not None:
                    check_definition_unchanged(object, current)
                if object.is_published:
                    check_publishable(object, current)
                registered.append((object, current))

        # Attribute groups can't be unpublished while a published predictive attribute
        # uses them, so take predictive attributes off the engines first
        for predictive_attribute, current in registered:
            if not predictive_attribute.is_published and current is not None:
                self.predictive_attributes.unpublish(current=current)

        # First publish all attribute keys in case they are dependencies of attribute groups
        for object in objects:
            if isinstance(object, AttributeKey):
                updated_objects.append(
                    self._create_or_update_attribute_key(attribute_key=object)
                )

        # Publish all attribute groups in case they are dependencies of services
        for object in objects:
            if isinstance(object, AttributeGroup):
                updated_objects.append(
                    self._create_or_update_attribute_group(attribute_group=object)
                )

        for object in objects:
            if isinstance(object, Service):
                updated_objects.append(self._create_or_update_service(service=object))

        for object in objects:
            if isinstance(object, RuleIntervention):
                updated_objects.append(
                    self._create_or_update_intervention(intervention=object)
                )

        # Event logs depend on attribute keys, so publish them after the keys
        for object in objects:
            if isinstance(object, EventLog):
                updated_objects.append(
                    self._create_or_update_event_log(event_log=object)
                )

        # Predictive attributes reference attribute groups, so register them last
        for object in objects:
            if isinstance(object, PredictiveAttribute):
                updated_objects.append(
                    self._create_or_update_predictive_attribute(
                        predictive_attribute=object
                    )
                )

        return updated_objects

    def delete(self, objects: list[RegistryObject]) -> None:
        """
        Deletes the provided objects from the Signals registry.
        """
        # Predictive attributes reference attribute groups, so delete them first
        for object in objects:
            if isinstance(object, PredictiveAttribute):
                self.predictive_attributes.delete(object)

        for object in objects:
            if isinstance(object, EventLog):
                self._delete_event_log(event_log=object)

        for object in objects:
            if isinstance(object, RuleIntervention):
                self._delete_intervention(intervention=object)

        for object in objects:
            if isinstance(object, Service):
                self._delete_service(service=object)

        for object in objects:
            if isinstance(object, AttributeGroup):
                self._delete_attribute_group(attribute_group=object)

        for object in objects:
            if isinstance(object, AttributeKey):
                self._delete_attribute_key(attribute_key=object)

    def get_attribute_group(
        self, name: str, version: int | None = None
    ) -> AttributeGroupResponse:
        if version is not None:
            response = self.api_client.make_request(
                method="GET",
                endpoint=(f"registry/attribute_groups/{name}/versions/{version}"),
            )
        else:
            response = self.api_client.make_request(
                method="GET",
                endpoint=(f"registry/attribute_groups/{name}"),
            )

        return AttributeGroupResponse.model_validate(response)

    def get_service(self, name: str) -> Service:
        response = self.api_client.make_request(
            method="GET",
            endpoint=(f"registry/services/{name}"),
        )
        return Service.model_validate(response)

    def get_event_log(self, name: str) -> EventLogResponse:
        response = self.api_client.make_request(
            method="GET",
            endpoint=(f"registry/event_logs/{name}"),
        )
        return EventLogResponse.model_validate(response)

    def _create_or_update_attribute_group(
        self, attribute_group: AttributeGroup
    ) -> AttributeGroup:
        try:
            response = self.api_client.make_request(
                method="POST",
                endpoint="registry/attribute_groups/",
                data=self._model_dump(attribute_group),
            )
        except SignalsAPIError as e:
            if e.status_code == 400:
                response = self.api_client.make_request(
                    method="PUT",
                    endpoint=(
                        f"registry/attribute_groups/{attribute_group.name}/versions/{attribute_group.version}"
                    ),
                    data=self._model_dump(attribute_group),
                )
            else:
                raise e

        return AttributeGroup.model_validate(response)

    def _create_or_update_service(self, service: Service) -> Service:
        try:
            response = self.api_client.make_request(
                method="POST",
                endpoint="registry/services/",
                data=self._model_dump(service),
            )
        except SignalsAPIError as e:
            if e.status_code == 400:
                response = self.api_client.make_request(
                    method="PUT",
                    endpoint=(f"registry/services/{service.name}"),
                    data=self._model_dump(service),
                )
            else:
                raise e

        return Service.model_validate(response)

    def _create_or_update_intervention(
        self, intervention: RuleIntervention
    ) -> RuleIntervention:
        try:
            response = self.api_client.make_request(
                method="POST",
                endpoint="registry/interventions/",
                data=self._model_dump(intervention),
            )
        except SignalsAPIError as e:
            if e.status_code == 400:
                response = self.api_client.make_request(
                    method="PUT",
                    endpoint=(
                        f"registry/interventions/{intervention.name}/versions/{intervention.version}"
                    ),
                    data=self._model_dump(intervention),
                )
            else:
                raise e

        return RuleIntervention.model_validate(response)

    def _create_or_update_event_log(self, event_log: EventLog) -> EventLog:
        # is_published is a client-side control for engine promotion and is not
        # part of the event_logs registry input schema (unlike the other
        # registry types), so it must not be sent to the registry endpoint.
        payload = self._model_dump(event_log)
        payload.pop("is_published", None)

        try:
            response = self.api_client.make_request(
                method="POST",
                endpoint="registry/event_logs/",
                data=payload,
            )
        except SignalsAPIError as e:
            if e.status_code == 400:
                response = self.api_client.make_request(
                    method="PUT",
                    endpoint=(f"registry/event_logs/{event_log.name}"),
                    data=payload,
                )
            else:
                raise e

        # Unlike other registry types, the event_logs endpoint does not promote
        # the resource to the engines based on is_published. We need to call the
        # engines publish/unpublish endpoint explicitly as a second step.
        if event_log.is_published:
            self._publish_event_log_to_engines(event_log=event_log)
        else:
            self._unpublish_event_log_from_engines(event_log=event_log)

        # The registry response has no is_published field, so preserve the
        # requested publish state on the returned wrapper.
        updated = EventLog.model_validate(response)
        updated.is_published = event_log.is_published
        return updated

    def _create_or_update_predictive_attribute(
        self, predictive_attribute: PredictiveAttribute
    ) -> PredictiveAttribute:
        response = self.predictive_attributes.create(predictive_attribute)

        # Like event logs, predictive attributes are promoted to the engines by a
        # separate call. If it is already published, the live training is left as is;
        # use Signals.publish_predictive_attribute to change it. Unpublishing already
        # happened before the attribute groups were updated.
        if predictive_attribute.is_published:
            if response.is_published:
                warn_if_newer_training(response)
            else:
                self.predictive_attributes.publish(current=response)

        return predictive_attribute

    def _publish_event_log_to_engines(self, event_log: EventLog) -> None:
        request = SelectivePublishRequest(
            event_logs=[EventLogReference(name=event_log.name)]
        )
        self.api_client.make_request(
            method="POST",
            endpoint="engines/publish",
            data=self._model_dump(request),
        )

    def _unpublish_event_log_from_engines(self, event_log: EventLog) -> None:
        request = UnpublishRequest(event_logs=[EventLogReference(name=event_log.name)])
        self.api_client.make_request(
            method="POST",
            endpoint="engines/unpublish",
            data=self._model_dump(request),
        )

    def _create_or_update_attribute_key(
        self, attribute_key: AttributeKey
    ) -> AttributeKey:
        try:
            response = self.api_client.make_request(
                method="POST",
                endpoint="registry/attribute_keys/",
                data=self._model_dump(attribute_key),
            )
        except SignalsAPIError as e:
            if e.status_code == 400:
                response = self.api_client.make_request(
                    method="PUT",
                    endpoint=(f"registry/attribute_keys/{attribute_key.name}"),
                    data=self._model_dump(attribute_key),
                )
            else:
                raise e

        return AttributeKey.model_validate(response)

    def _delete_attribute_group(self, attribute_group: AttributeGroup) -> None:

        self.api_client.make_request(
            method="DELETE",
            endpoint=(
                f"registry/attribute_groups/{attribute_group.name}/versions/{attribute_group.version}"
            ),
        )

    def _delete_service(self, service: Service) -> None:
        self.api_client.make_request(
            method="DELETE",
            endpoint=(f"registry/services/{service.name}"),
        )

    def _delete_intervention(self, intervention: RuleIntervention) -> None:
        self.api_client.make_request(
            method="DELETE",
            endpoint=(
                f"registry/interventions/{intervention.name}/versions/{intervention.version}"
            ),
        )

    def _delete_attribute_key(self, attribute_key: AttributeKey) -> None:
        self.api_client.make_request(
            method="DELETE",
            endpoint=(f"registry/attribute_keys/{attribute_key.name}"),
        )

    def _delete_event_log(self, event_log: EventLog) -> None:
        self.api_client.make_request(
            method="DELETE",
            endpoint=(f"registry/event_logs/{event_log.name}"),
        )

    def _model_dump(self, model: BaseModel) -> dict:
        return model.model_dump(
            mode="json",
            exclude_none=True,
            by_alias=True,
        )
