import httpx
import pytest
from respx import MockRouter

from snowplow_signals.api_client import ApiClient, SignalsAPIError
from snowplow_signals.attributes_client import AttributesClient
from snowplow_signals.models import GetAttributesResponse


class TestAttributesClient:
    def test_get_attributes(self, respx_mock: MockRouter, api_client: ApiClient):
        attributes_client = AttributesClient(api_client=api_client)
        identifier = "user-123"

        api_request_response = GetAttributesResponse(
            data={
                "domain_userid": ["user-123"],
                "page_views_count": [10],
            }
        )

        # Capture and verify the request structure uses new GetViewAttributesRequest model
        def check_group_request(request):
            import json

            body = json.loads(request.content)
            # Verify GetViewAttributesRequest structure
            assert "attribute_keys" in body
            assert body["attribute_keys"]["domain_userid"] == ["user-123"]
            assert "attributes" in body
            assert body["attributes"] == ["my_attribute_group_v1:page_views_count"]
            # Should NOT have "service" field for view requests
            assert "service" not in body
            return httpx.Response(200, json=api_request_response.data)

        respx_mock.post("http://localhost:8000/api/v1/get-online-attributes").mock(
            side_effect=check_group_request
        )

        response = attributes_client.get_group_attributes(
            name="my_attribute_group",
            version=1,
            attribute_key="domain_userid",
            identifier=identifier,
            attributes="page_views_count",
        )

        sdk_expected_response = {
            "domain_userid": "user-123",
            "page_views_count": 10,
        }

        assert response == sdk_expected_response

    def test_get_service_attributes(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        attributes_client = AttributesClient(api_client=api_client)
        identifier = "user-123"

        api_request_response = GetAttributesResponse(
            data={
                "domain_userid": ["user-123"],
                "page_views_count": [10],
            }
        )

        # Capture and verify the request structure uses new GetServiceAttributesRequest model
        def check_service_request(request):
            import json

            body = json.loads(request.content)
            # Verify GetServiceAttributesRequest structure with AttributeKeyIdentifiers wrapper
            assert "attribute_keys" in body
            assert body["attribute_keys"]["domain_userid"] == ["user-123"]
            assert "service" in body
            assert body["service"] == "my_service"
            # Should NOT have "attributes" field for service requests
            assert "attributes" not in body
            return httpx.Response(200, json=api_request_response.data)

        respx_mock.post("http://localhost:8000/api/v1/get-online-attributes").mock(
            side_effect=check_service_request
        )

        response = attributes_client.get_service_attributes(
            name="my_service",
            attribute_key="domain_userid",
            identifier=identifier,
        )

        sdk_expected_response = {
            "domain_userid": "user-123",
            "page_views_count": 10,
        }

        assert response == sdk_expected_response

    def test_get_agentic_context(self, respx_mock: MockRouter, api_client: ApiClient):
        attributes_client = AttributesClient(api_client=api_client)

        api_response = {
            "attribute_key": "domain_sessionid",
            "identifier": "session-123",
            "name": "my_event_log",
            "prompt": "some prompt",
            "summary": "a short summary of the buffered events",
            "started_at_ms": 1700000000000,
            "version": 1,
            "events": [{"event_name": "page_view", "page_url": "https://example.com"}],
        }

        def check_request(request):
            assert request.url.params["name"] == "my_event_log"
            assert request.url.params["identifier"] == "session-123"
            assert request.url.params["format"] == "json"
            return httpx.Response(200, json=api_response)

        respx_mock.get("http://localhost:8000/api/v1/event_log").mock(
            side_effect=check_request
        )

        response = attributes_client.get_agentic_context(
            name="my_event_log",
            identifier="session-123",
        )

        assert response.name == "my_event_log"
        assert response.identifier == "session-123"
        assert response.attribute_key == "domain_sessionid"
        assert response.summary == "a short summary of the buffered events"
        assert response.events == [
            {"event_name": "page_view", "page_url": "https://example.com"}
        ]

    def test_get_agentic_context_narrative(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        attributes_client = AttributesClient(api_client=api_client)

        narrative = "Session session-123 viewed https://example.com"

        def check_request(request):
            assert request.url.params["name"] == "my_event_log"
            assert request.url.params["identifier"] == "session-123"
            assert request.url.params["format"] == "narrative"
            return httpx.Response(
                200, text=narrative, headers={"Content-Type": "text/plain"}
            )

        respx_mock.get("http://localhost:8000/api/v1/event_log").mock(
            side_effect=check_request
        )

        response = attributes_client.get_agentic_context(
            name="my_event_log",
            identifier="session-123",
            format="narrative",
        )

        assert response == narrative

    def test_get_agentic_context_not_found(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        attributes_client = AttributesClient(api_client=api_client)

        respx_mock.get("http://localhost:8000/api/v1/event_log").mock(
            return_value=httpx.Response(404, json={"error": "event log name not found"})
        )

        with pytest.raises(SignalsAPIError) as exc_info:
            attributes_client.get_agentic_context(
                name="missing_event_log",
                identifier="session-123",
            )

        assert exc_info.value.status_code == 404

    def test_get_attributes_multiple_attributes(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        """Test that multiple attributes are properly formatted in arribute group requests."""
        attributes_client = AttributesClient(api_client=api_client)
        identifier = "user-111"

        api_request_response = GetAttributesResponse(
            data={
                "domain_userid": ["user-111"],
                "page_views": [25],
                "session_duration": [1800],
                "bounce_rate": [0.2],
            }
        )

        # Verify multiple attributes formatting
        def check_multiple_attributes(request):
            import json

            body = json.loads(request.content)
            expected_attributes = [
                "analytics_v1:page_views",
                "analytics_v1:session_duration",
                "analytics_v1:bounce_rate",
            ]
            assert body["attributes"] == expected_attributes
            return httpx.Response(200, json=api_request_response.data)

        respx_mock.post("http://localhost:8000/api/v1/get-online-attributes").mock(
            side_effect=check_multiple_attributes
        )

        response = attributes_client.get_group_attributes(
            name="analytics",
            version=1,
            attribute_key="domain_userid",
            identifier=identifier,
            attributes=["page_views", "session_duration", "bounce_rate"],
        )

        expected_response = {
            "domain_userid": "user-111",
            "page_views": 25,
            "session_duration": 1800,
            "bounce_rate": 0.2,
        }

        assert response == expected_response
