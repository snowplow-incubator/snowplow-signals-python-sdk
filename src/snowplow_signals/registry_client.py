from pydantic import BaseModel

from .api_client import ApiClient, SignalsAPIError
from .models import Entity, RuleIntervention, Service, View, ViewResponse


class RegistryClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def apply(
        self, objects: list[View | Service | Entity | RuleIntervention]
    ) -> list[View | Service | Entity | RuleIntervention]:
        updated_objects: list[View | Service | Entity | RuleIntervention] = []

        # First apply all entities in case they are dependencies of views
        for object in objects:
            if isinstance(object, Entity):
                updated_objects.append(self._create_or_update_entity(entity=object))

        # Apply all views in case they are dependencies of services
        for object in objects:
            if isinstance(object, View):
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

    def get_view(self, name: str, version: int | None = None) -> ViewResponse:
        if version is not None:
            response = self.api_client.make_request(
                method="GET",
                endpoint=(f"registry/views/{name}/versions/{version}"),
            )
        else:
            response = self.api_client.make_request(
                method="GET",
                endpoint=(f"registry/views/{name}"),
            )

        return ViewResponse.model_validate(response)

    def get_service(self, name: str) -> Service:
        response = self.api_client.make_request(
            method="GET",
            endpoint=(f"registry/services/{name}"),
        )
        return Service.model_validate(response)

    def _create_or_update_view(self, view: View) -> View:
        try:
            response = self.api_client.make_request(
                method="POST",
                endpoint="registry/views/",
                data=self._model_dump(view),
            )
        except SignalsAPIError as e:
            if e.status_code == 400:
                response = self.api_client.make_request(
                    method="PUT",
                    endpoint=(f"registry/views/{view.name}/versions/{view.version}"),
                    data=self._model_dump(view),
                )
            else:
                raise e

        return View.model_validate(response)

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

    def _create_or_update_entity(self, entity: Entity) -> Entity:
        try:
            response = self.api_client.make_request(
                method="POST",
                endpoint="registry/entities/",
                data=self._model_dump(entity),
            )
        except SignalsAPIError as e:
            if e.status_code == 400:
                response = self.api_client.make_request(
                    method="PUT",
                    endpoint=(f"registry/entities/{entity.name}"),
                    data=self._model_dump(entity),
                )
            else:
                raise e

        return Entity.model_validate(response)

    def _model_dump(self, model: BaseModel) -> dict:
        return model.model_dump(
            mode="json",
            exclude_none=True,
            by_alias=True,
        )
