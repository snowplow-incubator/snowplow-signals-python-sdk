import json
from datetime import timedelta

import httpx
import pytest

from snowplow_signals import (
    Attribute,
    BatchSource,
    Event,
    LinkEntity,
    View,
    domain_userid,
)
from snowplow_signals.models import ViewResponse
from snowplow_signals.api_client import ApiClient
from snowplow_signals.models import ViewResponse
from snowplow_signals.registry_client import RegistryClient

from .utils import MOCK_ORG_ID


class TestRegistryClient:
    @pytest.fixture
    def api_client(self):
        return ApiClient(
            api_url="http://localhost:8000",
            api_key="foo",
            api_key_id="bar",
            org_id=MOCK_ORG_ID,
        )

    def test_serializes_period_correctly_using_iso_format(self, respx_mock, api_client):
        view = View(
            name="my_view",
            entity=domain_userid,
            owner="test@example.com",
            attributes=[
                Attribute(
                    name="add_to_cart_events_count",
                    type="int32",
                    events=[
                        Event(
                            vendor="com.snowplowanalytics.snowplow.ecommerce",
                            name="snowplow_ecommerce_action",
                            version="1-0-2",
                        )
                    ],
                    aggregation="counter",
                    period=timedelta(days=1),
                )
            ],
        )
        view_output = ViewResponse(
            name="my_view",
            entity=LinkEntity(name="user"),
            feast_name="my_view_v1",
            offline=True,
            stream_source_name="my_stream",
            entity_key="user_id",
            view_or_entity_ttl=None,
            owner="test@example.com",
        )

        view_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/views/"
        ).mock(return_value=httpx.Response(201, json=view_output.model_dump()))

        registry_client = RegistryClient(api_client=api_client)
        registry_client.apply([view])

        assert view_mock.called
        assert "P1D" in str(view_mock.calls[0].request.content)

    def test_serializes_batch_source_correctly(self, respx_mock, api_client):
        view = View(
            name="my_view",
            entity=domain_userid,
            owner="test@example.com",
            attributes=[
                Attribute(
                    name="add_to_cart_events_count",
                    type="int32",
                    events=[
                        Event(
                            vendor="com.snowplowanalytics.snowplow.ecommerce",
                            name="snowplow_ecommerce_action",
                            version="1-0-2",
                        )
                    ],
                    aggregation="counter",
                )
            ],
            batch_source=BatchSource(
                name="my_batch_source",
                database="my_database",
                schema="my_schema",
                table="my_table",
            ),
        )
        view_output = ViewResponse(
            name="my_view",
            entity=LinkEntity(name="user"),
            feast_name="my_view_v1",
            offline=True,
            stream_source_name="my_stream",
            entity_key="user_id",
            view_or_entity_ttl=None,
            owner="test@example.com",
        )

        view_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/views/"
        ).mock(return_value=httpx.Response(201, json=view_output.model_dump()))

        registry_client = RegistryClient(api_client=api_client)
        registry_client.apply([view])

        assert view_mock.called
        request_content = json.loads(view_mock.calls[0].request.content)
        assert request_content["batch_source"]["database"] == "my_database"
        assert request_content["batch_source"]["table"] == "my_table"
        assert request_content["batch_source"]["schema"] == "my_schema"

    def test_api_url_with_trailing_slash(self, respx_mock):
        """Test that ApiClient works with a trailing slash in api_url."""
        api_client = ApiClient(
            api_url="http://localhost:8000/",
            api_key="foo",
            api_key_id="bar",
            org_id=MOCK_ORG_ID,
        )
        view = View(
            name="my_view",
            entity=domain_userid,
            owner="test@example.com",
            attributes=[],
        )
        view_output = ViewResponse(
            name="my_view",
            entity=LinkEntity(name="user"),
            feast_name="my_view_v1",
            offline=True,
            stream_source_name="my_stream",
            entity_key="user_id",
            view_or_entity_ttl=None,
            owner="test@example.com",
        )
        view_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/views/"
        ).mock(return_value=httpx.Response(201, json=view_output.model_dump()))
        registry_client = RegistryClient(api_client=api_client)
        registry_client.apply([view])
        assert view_mock.called
