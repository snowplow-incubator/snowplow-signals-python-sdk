from typing import Any, Literal

from .api_client import ApiClient
from .models import (
    AttributeKeyIdentifiers,
    EventLogBufferResponse,
    GetAttributeGroupAttributesRequest,
    GetAttributesResponse,
    GetServiceAttributesRequest,
)


class AttributesClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def get_group_attributes(
        self,
        name: str,
        version: int,
        attributes: list[str] | str,
        attribute_key: str,
        identifier: str,
    ) -> dict[str, Any]:
        attributes = (
            [f"{name}_v{version}:{attribute}" for attribute in attributes]
            if isinstance(attributes, list)
            else [f"{name}_v{version}:{attributes}"]
        )
        attribute_key_identifiers = AttributeKeyIdentifiers(
            root={attribute_key: [identifier]}
        )

        request = GetAttributeGroupAttributesRequest(
            attributes=attributes,
            attribute_keys=attribute_key_identifiers,
        )
        return self._make_request(request)

    def get_service_attributes(
        self,
        name: str,
        attribute_key: str,
        identifier: str,
    ) -> dict[str, Any]:
        attribute_key_identifiers = AttributeKeyIdentifiers(
            root={attribute_key: [identifier]}
        )

        request = GetServiceAttributesRequest(
            service=name,
            attribute_keys=attribute_key_identifiers,
        )
        return self._make_request(request)

    def get_event_log(
        self,
        name: str,
        identifier: str,
        format: Literal["json", "narrative"] = "json",
    ) -> EventLogBufferResponse | str:
        """
        Retrieves the buffered events for a given event log by name.

        Args:
            name: The name of the event log.
            identifier: The attribute key value identifying the entity.
            format: The response format. "json" (default) returns a structured
                EventLogBufferResponse; "narrative" returns an LLM-ready
                plain-text context block.
        """
        params = {"name": name, "identifier": identifier, "format": format}
        if format == "narrative":
            return self.api_client.make_text_request(
                method="GET",
                endpoint="event_log",
                params=params,
            )
        response = self.api_client.make_request(
            method="GET",
            endpoint="event_log",
            params=params,
        )
        return EventLogBufferResponse.model_validate(response)

    def _make_request(
        self, request: GetAttributeGroupAttributesRequest | GetServiceAttributesRequest
    ) -> dict[str, Any]:
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
