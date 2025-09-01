import httpx
from respx import MockRouter

from snowplow_signals.api_client import ApiClient
from snowplow_signals.attributes_client import AttributesClient
from snowplow_signals.models import GetAttributesResponse


class TestAttributesClient:
    def test_get_view_attributes(self, respx_mock: MockRouter, api_client: ApiClient):
        attributes_client = AttributesClient(api_client=api_client)
        identifier = "user-123"

        api_request_response = GetAttributesResponse(
            data={
                "domain_userid": ["user-123"],
                "page_views_count": [10],
            }
        )

        # Capture and verify the request structure uses new GetViewAttributesRequest model
        def check_view_request(request):
            import json

            body = json.loads(request.content)
            # Verify GetViewAttributesRequest structure
            assert "entities" in body
            assert body["entities"]["domain_userid"] == ["user-123"]
            assert "attributes" in body
            assert body["attributes"] == ["page_views_count"]
            # Should NOT have "service" field for view requests
            assert "service" not in body
            return httpx.Response(200, json=api_request_response.data)

        respx_mock.post("http://localhost:8000/api/v1/get-online-attributes").mock(
            side_effect=check_view_request
        )

        response = attributes_client.get_view_attributes(
            name="my_view",
            version=1,
            entity="domain_userid",
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
            assert "entities" in body
            assert body["entities"]["domain_userid"] == ["user-123"]
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
            entity="domain_userid",
            identifier=identifier,
        )

        sdk_expected_response = {
            "domain_userid": "user-123",
            "page_views_count": 10,
        }

        assert response == sdk_expected_response

    def test_get_view_attributes_multiple_attributes(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        """Test that multiple attributes are properly formatted in view requests."""
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

        response = attributes_client.get_view_attributes(
            name="analytics",
            version=1,
            entity="domain_userid",
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
