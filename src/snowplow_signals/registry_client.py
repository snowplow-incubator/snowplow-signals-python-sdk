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

        # First apply all entities in case they are dependencies of views
        for object in objects:
            if isinstance(object, AttributeKey):
                updated_objects.append(self._create_or_update_entity(entity=object))

        # Apply all views in case they are dependencies of services
        for object in objects:
            if isinstance(object, AttributeGroup):
                updated_objects.append(self._create_or_update_view(view=object))

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
                self._delete_view(view=object)

        for object in objects:
            if isinstance(object, AttributeKey):
                self._delete_entity(entity=object)

    def get_view(self, name: str, version: int | None = None) -> AttributeGroupResponse:
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

    def _create_or_update_view(self, view: AttributeGroup) -> AttributeGroup:
        try:
            response = self.api_client.make_request(
                method="POST",
                endpoint="registry/attribute_groups/",
                data=self._model_dump(view),
            )
        except SignalsAPIError as e:
            if e.status_code == 400:
                response = self.api_client.make_request(
                    method="PUT",
                    endpoint=(
                        f"registry/attribute_groups/{view.name}/versions/{view.version}"
                    ),
                    data=self._model_dump(view),
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

    def _create_or_update_entity(self, entity: AttributeKey) -> AttributeKey:
        try:
            response = self.api_client.make_request(
                method="POST",
                endpoint="registry/attribute_keys/",
                data=self._model_dump(entity),
            )
        except SignalsAPIError as e:
            if e.status_code == 400:
                response = self.api_client.make_request(
                    method="PUT",
                    endpoint=(f"registry/attribute_keys/{entity.name}"),
                    data=self._model_dump(entity),
                )
            else:
                raise e

        return AttributeKey.model_validate(response)

    def _delete_view(self, view: AttributeGroup) -> None:

        self.api_client.make_request(
            method="DELETE",
            endpoint=(f"registry/attribute_groups/{view.name}/versions/{view.version}"),
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

    def _delete_entity(self, entity: AttributeKey) -> None:
        self.api_client.make_request(
            method="DELETE",
            endpoint=(f"registry/attribute_keys/{entity.name}"),
        )

    def _model_dump(self, model: BaseModel) -> dict:
        return model.model_dump(
            mode="json",
            exclude_none=True,
            by_alias=True,
        )
