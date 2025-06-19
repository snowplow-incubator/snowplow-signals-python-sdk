import httpx

from snowplow_signals.attributes_client import AttributesClient
from snowplow_signals.models import GetAttributesResponse


class TestAttributesClient:

    def test_get_view_attributes(self, respx_mock, api_client):
        attributes_client = AttributesClient(api_client=api_client)
        identifier = "user-123"

        api_request_response = GetAttributesResponse(
            data={
                "domain_userid": ["user-123"],
                "page_views_count": [10],
            }
        )

        respx_mock.post("http://localhost:8000/api/v1/get-online-attributes").mock(
            return_value=httpx.Response(200, json=api_request_response.data)
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

    def test_get_service_attributes(self, respx_mock, api_client):
        attributes_client = AttributesClient(api_client=api_client)
        identifier = ["user-123"]

        api_request_response = GetAttributesResponse(
            data={
                "domain_userid": ["user-123"],
                "page_views_count": [10],
            }
        )

        respx_mock.post("http://localhost:8000/api/v1/get-online-attributes").mock(
            return_value=httpx.Response(200, json=api_request_response.data)
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
