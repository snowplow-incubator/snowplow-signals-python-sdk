import httpx
import pytest

from snowplow_signals import (
    LinkEntity,
    Service,
    View,
    session_entity,
    user_entity,
)
from snowplow_signals.api_client import ApiClient
from snowplow_signals.attributes_client import AttributesClient
from snowplow_signals.models import ViewOutput

from .utils import MOCK_ORG_ID


class TestAttributesClient:
    @pytest.fixture
    def api_client(self):
        return ApiClient(
            api_url="http://localhost:8000",
            api_key="foo",
            api_key_id="bar",
            org_id=MOCK_ORG_ID,
        )

    def test_get_entity_name_with_single_entity(self, respx_mock, api_client):
        user_view_a = View(
            name="user_view_a",
            entity=user_entity,
        )
        user_view_b = View(
            name="user_view_b",
            entity=user_entity,
        )

        user_view_a_output = ViewOutput(
            name="user_view_a",
            entity=LinkEntity(name="user"),
            feast_name="user_view_a_v1",
            offline=True,
            stream_source_name="my_stream",
            entity_key="user_id",
            view_or_entity_ttl=None,
        )
        user_view_b_output = ViewOutput(
            name="user_view_b_output",
            entity=LinkEntity(name="user"),
            feast_name="user_view_b_v1",
            offline=True,
            stream_source_name="my_stream",
            entity_key="user_id",
            view_or_entity_ttl=None,
        )
        attributes_client = AttributesClient(api_client=api_client)

        respx_mock.get(
            "http://localhost:8000/api/v1/registry/views/user_view_a/versions/1"
        ).mock(return_value=httpx.Response(201, json=user_view_a_output.model_dump()))

        respx_mock.get(
            "http://localhost:8000/api/v1/registry/views/user_view_b/versions/1"
        ).mock(return_value=httpx.Response(201, json=user_view_b_output.model_dump()))

        service = Service(
            name="my_service",
            views=[user_view_a, user_view_b],
        )
        entity = attributes_client._get_entity_name(service=service)
        assert entity == "user"

    def test_get_entity_name_with_multiple_entities(self, respx_mock, api_client):
        user_view = View(
            name="user_view",
            entity=user_entity,
        )
        session_view = View(
            name="session_view",
            entity=session_entity,
        )
        user_view_output = ViewOutput(
            name="user_view",
            entity=LinkEntity(name="user"),
            feast_name="user_view_v1",
            offline=True,
            stream_source_name="my_stream",
            entity_key="user_id",
            view_or_entity_ttl=None,
        )
        session_view_output = ViewOutput(
            name="session_view",
            entity=LinkEntity(name="session"),
            feast_name="session_view_v1",
            offline=True,
            stream_source_name="my_stream",
            entity_key="domain_sessionid",
            view_or_entity_ttl=None,
        )
        attributes_client = AttributesClient(api_client=api_client)

        respx_mock.get(
            "http://localhost:8000/api/v1/registry/views/user_view/versions/1"
        ).mock(return_value=httpx.Response(201, json=user_view_output.model_dump()))

        respx_mock.get(
            "http://localhost:8000/api/v1/registry/views/session_view/versions/1"
        ).mock(return_value=httpx.Response(201, json=session_view_output.model_dump()))

        service = Service(
            name="my_service",
            views=[user_view, session_view],
        )
        with pytest.raises(
            ValueError,
            match="The service contains views with different entities which is not supported.",
        ):
            attributes_client._get_entity_name(service=service)
