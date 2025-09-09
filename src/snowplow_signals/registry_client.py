from pydantic import BaseModel

from .api_client import ApiClient, SignalsAPIError
from .models import (
    AttributeGroup,
    AttributeGroupResponse,
    AttributeKey,
    RuleIntervention,
    Service,
)


class RegistryClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def create_or_update(
        self, objects: list[AttributeGroup | Service | AttributeKey | RuleIntervention]
    ) -> list[AttributeGroup | Service | AttributeKey | RuleIntervention]:
        updated_objects: list[
            AttributeGroup | Service | AttributeKey | RuleIntervention
        ] = []

        # First publish all attribute keys in case they are dependencies of attribute groups
        for object in objects:
            if isinstance(object, AttributeKey):
                updated_objects.append(self._create_or_update_attribute_key(attribute_key=object))

        # Publish all attribute groups in case they are dependencies of services
        for object in objects:
            if isinstance(object, AttributeGroup):
                updated_objects.append(self._create_or_update_attribute_group(attribute_group=object))

        for object in objects:
            if isinstance(object, Service):
                updated_objects.append(self._create_or_update_service(service=object))

        for object in objects:
            if isinstance(object, RuleIntervention):
                updated_objects.append(
                    self._create_or_update_intervention(intervention=object)
                )

        return updated_objects

    def delete(
        self, objects: list[AttributeGroup | Service | AttributeKey | RuleIntervention]
    ) -> None:
        """
        Deletes the provided objects from the Signals registry.
        """
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

    def get_attribute_group(self, name: str, version: int | None = None) -> AttributeGroupResponse:
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

    def _create_or_update_attribute_group(self, attribute_group: AttributeGroup) -> AttributeGroup:
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

    def _create_or_update_attribute_key(self, attribute_key: AttributeKey) -> AttributeKey:
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
            endpoint=(f"registry/attribute_groups/{attribute_group.name}/versions/{attribute_group.version}"),
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

    def _model_dump(self, model: BaseModel) -> dict:
        return model.model_dump(
            mode="json",
            exclude_none=True,
            by_alias=True,
        )
