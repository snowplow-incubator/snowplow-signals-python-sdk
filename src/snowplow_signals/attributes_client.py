from .api_client import ApiClient
from .models import (
    GetOnlineAttributesRequest,
    OnlineAttributesResponse,
    Service,
    View,
    ViewResponse,
)
from .registry_client import RegistryClient


class AttributesClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def get_view_attributes(
        self,
        view: View | ViewResponse,
        identifiers: list[str] | str,
    ) -> OnlineAttributesResponse:
        attributes = [
            f"{view.name}_v{view.version}:{attribute.name}"
            for attribute in (view.attributes or []) + (view.fields or [])
        ]

        request = GetOnlineAttributesRequest(
            attributes=attributes,
            entities={
                view.entity.name: (
                    identifiers if isinstance(identifiers, list) else [identifiers]
                )
            },
        )
        return self._make_request(request)

    def _get_entity_name(self, service: Service) -> str:
        unique_entity_names: set[str] = set()
        for view in service.views:
            fetched_view = RegistryClient(api_client=self.api_client).get_view(
                name=view.name, version=view.version
            )
            unique_entity_names.add(fetched_view.entity.name)

        if len(unique_entity_names) > 1:
            raise ValueError(
                "The service contains views with different entities which is not supported."
            )

        return unique_entity_names.pop()

    def get_service_attributes(
        self,
        service: Service,
        identifiers: list[str] | str,
    ) -> OnlineAttributesResponse:
        if not service.views:
            raise ValueError("No views to fetch.")

        entity_name = self._get_entity_name(service=service)
        request = GetOnlineAttributesRequest(
            service=service.name,
            entities={
                entity_name: (
                    identifiers if isinstance(identifiers, list) else [identifiers]
                )
            },
        )
        return self._make_request(request)

    def _make_request(
        self, request: GetOnlineAttributesRequest
    ) -> OnlineAttributesResponse:
        response = self.api_client.make_request(
            method="POST",
            endpoint="get-online-attributes",
            data=request.model_dump(mode="json"),
        )
        return OnlineAttributesResponse(data=response)
