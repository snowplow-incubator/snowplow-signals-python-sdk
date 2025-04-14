from .api_client import ApiClient, SignalsAPIError
from .models import Service, View, ViewOutput


class RegistryClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def apply(self, objects: list[View | Service]) -> list[ViewOutput | Service]:
        updated_objects: list[View | Service] = []

        # First apply all views in case they are dependencies of services
        for object in objects:
            if isinstance(object, View):
                updated_objects.append(self._create_or_update_view(view=object))

        for object in objects:
            if isinstance(object, Service):
                updated_objects.append(self._create_or_update_service(service=object))

        return updated_objects

    def get_view(self, name: str, version: int | None = None) -> ViewOutput:
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

        return ViewOutput.model_validate(response)

    def _create_or_update_view(self, view: View) -> ViewOutput:
        try:
            response = self.api_client.make_request(
                method="POST",
                endpoint="registry/views/",
                data=view.model_dump(mode="json", exclude_none=True),
            )
        except SignalsAPIError as e:
            if e.status_code == 400:
                response = self.api_client.make_request(
                    method="PUT",
                    endpoint=(f"registry/views/{view.name}/versions/{view.version}"),
                    data=view.model_dump(mode="json", exclude_none=True),
                )
            else:
                raise e

        return ViewOutput.model_validate(response)

    def _create_or_update_service(self, service: Service) -> Service:
        try:
            response = self.api_client.make_request(
                method="POST",
                endpoint="registry/services/",
                data=service.model_dump(mode="json", exclude_none=True),
            )
        except SignalsAPIError as e:
            if e.status_code == 400:
                response = self.api_client.make_request(
                    method="PUT",
                    endpoint=(f"registry/services/{service.name}"),
                    data=service.model_dump(mode="json", exclude_none=True),
                )
            else:
                raise e

        return Service.model_validate(response)
