from typing import Any

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
    ) -> dict[str, Any]:

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
    ) -> dict[str, Any]:

        request = GetOnlineAttributesRequest(
            service=name,
            entities={entity: [identifier]},
        )
        return self._make_request(request)

    def _make_request(self, request: GetOnlineAttributesRequest) -> dict[str, Any]:
        response = self.api_client.make_request(
            method="POST",
            endpoint="get-online-attributes",
            data=request.model_dump(mode="json", exclude_none=True),
        )
        return _format_get_attributes_response(GetAttributesResponse(data=response))


def _format_get_attributes_response(response: GetAttributesResponse) -> dict[str, Any]:
    """
    Formats the GetAttributesResponse into a dictionary.

    Args:
        response: The GetAttributesResponse to format.

    Returns:
        A dictionary with attribute names as keys and lists of values.
    """
    result: dict[str, Any] = {}
    for key, value in response.data.items():
        if isinstance(value, list):
            result[key] = value[0] if value else None

    return result
