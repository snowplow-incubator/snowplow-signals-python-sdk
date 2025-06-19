from .api_client import ApiClient
from .models import (
    GetAttributesResponse,
    GetOnlineAttributesRequest,
)


class AttributesClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def get_view_attributes(
        self,
        name: str,
        version: int,
        attributes: list[str] | str,
        entity: str,
        identifier: str,
    ) -> GetAttributesResponse:

        attributes = (
            [f"{name}_v{version}:{attribute}" for attribute in attributes]
            if isinstance(attributes, list)
            else [attributes]
        )

        request = GetOnlineAttributesRequest(
            attributes=attributes,
            entities={entity: [identifier]},
        )
        return self._make_request(request)

    def get_service_attributes(
        self,
        name: str,
        entity: str,
        identifier: str,
    ) -> GetAttributesResponse:

        request = GetOnlineAttributesRequest(
            service=name,
            entities={entity: [identifier]},
        )
        return self._make_request(request)

    def _make_request(
        self, request: GetOnlineAttributesRequest
    ) -> GetAttributesResponse:
        response = self.api_client.make_request(
            method="POST",
            endpoint="get-online-attributes",
            data=request.model_dump(mode="json"),
        )
        return GetAttributesResponse(data=response)
