from pydantic import BaseModel

from .api_client import ApiClient, SignalsAPIError
from .models import (
    AttributeGroup,
    AttributeGroupResponse,
    AttributeKey,
    EventLog,
    EventLogReference,
    EventLogResponse,
    RuleIntervention,
    SelectivePublishRequest,
    Service,
    UnpublishRequest,
)

RegistryObject = AttributeGroup | Service | AttributeKey | RuleIntervention | EventLog


class RegistryClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def create_or_update(self, objects: list[RegistryObject]) -> list[RegistryObject]:
        updated_objects: list[RegistryObject] = []

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

        return updated_objects

    def delete(self, objects: list[RegistryObject]) -> None:
        """
        Deletes the provided objects from the Signals registry.
        """
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

    def get_event_log_definition(self, name: str) -> EventLogResponse:
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
        try:
            response = self.api_client.make_request(
                method="POST",
                endpoint="registry/event_logs/",
                data=self._model_dump(event_log),
            )
        except SignalsAPIError as e:
            if e.status_code == 400:
                response = self.api_client.make_request(
                    method="PUT",
                    endpoint=(f"registry/event_logs/{event_log.name}"),
                    data=self._model_dump(event_log),
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

        return EventLog.model_validate(response)

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
