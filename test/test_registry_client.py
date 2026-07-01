import json
from datetime import timedelta

import httpx
from respx import MockRouter

from snowplow_signals import (
    Attribute,
    AttributeGroup,
    BatchSource,
    Event,
    domain_userid,
)
from snowplow_signals.api_client import ApiClient
from snowplow_signals.models import AttributeGroupResponse, AttributeKeyOutput
from snowplow_signals.registry_client import RegistryClient

from .utils import MOCK_ORG_ID


class TestRegistryClient:
    def test_serializes_period_correctly_using_iso_format(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        attribute_group = AttributeGroup(
            name="my_attribute_group",
            attribute_key=domain_userid,
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
        group_output = AttributeGroupResponse(
            name="my_attribute_group",
            attribute_key=AttributeKeyOutput(name="user_id", blobl_path="user_id"),
            feast_name="my_attribute_group_v1",
            offline=True,
            stream_source_name="my_stream",
            attribute_key_or_name="user_id",
            attribute_group_or_attribute_key_ttl=None,
            owner="test@example.com",
            full_name="my_attribute_group_1",
        )

        group_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/attribute_groups/"
        ).mock(return_value=httpx.Response(201, json=group_output.model_dump()))

        registry_client = RegistryClient(api_client=api_client)
        registry_client.create_or_update([attribute_group])

        assert group_mock.called
        assert "P1D" in str(group_mock.calls[0].request.content)

    def test_serializes_batch_source_correctly(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        attribute_group = AttributeGroup(
            name="my_attribute_group",
            attribute_key=domain_userid,
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
                timestamp_field="timestamp_field",
            ),
        )
        group_output = AttributeGroupResponse(
            name="my_attribute_group",
            attribute_key=AttributeKeyOutput(name="user_id", blobl_path="user_id"),
            feast_name="my_attribute_group_v1",
            offline=True,
            stream_source_name="my_stream",
            attribute_key_or_name="user_id",
            attribute_group_or_attribute_key_ttl=None,
            owner="test@example.com",
            full_name="my_attribute_group_1",
        )

        group_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/attribute_groups/"
        ).mock(return_value=httpx.Response(201, json=group_output.model_dump()))

        registry_client = RegistryClient(api_client=api_client)
        registry_client.create_or_update([attribute_group])

        assert group_mock.called
        request_content = json.loads(group_mock.calls[0].request.content)
        assert request_content["batch_source"]["database"] == "my_database"
        assert request_content["batch_source"]["table"] == "my_table"
        assert request_content["batch_source"]["schema"] == "my_schema"

    def test_api_url_with_trailing_slash(self, respx_mock: MockRouter):
        """Test that ApiClient works with a trailing slash in api_url."""
        api_client = ApiClient(
            api_url="http://localhost:8000/",
            api_key="foo",
            api_key_id="bar",
            org_id=MOCK_ORG_ID,
        )
        attribute_group = AttributeGroup(
            name="my_attribute_group",
            attribute_key=domain_userid,
            owner="test@example.com",
            attributes=[],
        )
        group_output = AttributeGroupResponse(
            name="my_attribute_group",
            attribute_key=AttributeKeyOutput(name="user_id", blobl_path="user_id"),
            feast_name="my_attribute_group_v1",
            offline=True,
            stream_source_name="my_stream",
            attribute_key_or_name="user_id",
            attribute_group_or_attribute_key_ttl=None,
            owner="test@example.com",
            full_name="my_attribute_group_1",
        )
        group_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/attribute_groups/"
        ).mock(return_value=httpx.Response(201, json=group_output.model_dump()))
        registry_client = RegistryClient(api_client=api_client)
        registry_client.create_or_update([attribute_group])
        assert group_mock.called

    def test_delete_attribute_group(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        attribute_group = AttributeGroup(
            name="my_attribute_group",
            attribute_key=domain_userid,
            owner="test@example.com",
        )

        delete_mock = respx_mock.delete(
            "http://localhost:8000/api/v1/registry/attribute_groups/my_attribute_group/versions/1"
        ).mock(return_value=httpx.Response(200, json={}))

        registry_client = RegistryClient(api_client=api_client)
        registry_client.delete([attribute_group])

        assert delete_mock.called

    def test_delete_service(self, respx_mock: MockRouter, api_client: ApiClient):
        from snowplow_signals import Service

        service = Service(
            name="my_service",
            owner="test@example.com",
        )

        delete_mock = respx_mock.delete(
            "http://localhost:8000/api/v1/registry/services/my_service"
        ).mock(return_value=httpx.Response(200, json={}))

        registry_client = RegistryClient(api_client=api_client)
        registry_client.delete([service])

        assert delete_mock.called

    def test_delete_attribute_key(self, respx_mock: MockRouter, api_client: ApiClient):
        from snowplow_signals import AttributeKey

        attribute_key = AttributeKey(
            name="my_attribute_key",
        )

        delete_mock = respx_mock.delete(
            "http://localhost:8000/api/v1/registry/attribute_keys/my_attribute_key"
        ).mock(return_value=httpx.Response(200, json={}))

        registry_client = RegistryClient(api_client=api_client)
        registry_client.delete([attribute_key])

        assert delete_mock.called

    def _make_event_log(self, is_published: bool):
        from snowplow_signals import (
            EventLog,
            EventLogAtomicProperty,
            EventLogEvent,
            EventSelection,
        )
        from snowplow_signals.models import LinkAttributeKey

        return EventLog(
            name="my_event_log",
            attribute_key=LinkAttributeKey(name="domain_sessionid"),
            events=[
                EventSelection(
                    event=EventLogEvent(
                        name="page_view",
                        vendor="com.snowplowanalytics.snowplow",
                        version="1-0-0",
                    ),
                    properties=[EventLogAtomicProperty(name="page_url")],
                )
            ],
            max_events=10,
            max_age_seconds=600,
            is_published=is_published,
        )

    def test_publish_event_log_promotes_to_engines(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        event_log = self._make_event_log(is_published=True)

        # The registry response does not carry is_published (it is not part of
        # the event_logs input schema).
        registry_response = event_log.model_dump(mode="json", by_alias=True)
        registry_response.pop("is_published", None)
        create_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/event_logs/"
        ).mock(return_value=httpx.Response(201, json=registry_response))
        publish_mock = respx_mock.post(
            "http://localhost:8000/api/v1/engines/publish"
        ).mock(return_value=httpx.Response(200, json={}))

        registry_client = RegistryClient(api_client=api_client)
        [updated] = registry_client.create_or_update([event_log])

        assert create_mock.called
        request_content = json.loads(create_mock.calls[0].request.content)
        assert request_content["name"] == "my_event_log"
        assert request_content["attribute_key"]["name"] == "domain_sessionid"
        assert request_content["max_events"] == 10
        # is_published is a client-side control and must not be sent to the
        # event_logs registry endpoint.
        assert "is_published" not in request_content

        # The registry write must be followed by an explicit engines publish call
        assert publish_mock.called
        publish_content = json.loads(publish_mock.calls[0].request.content)
        assert publish_content["event_logs"] == [{"name": "my_event_log"}]

        # The requested publish state is preserved on the returned object even
        # though the registry response omits it.
        assert updated.is_published is True

    def test_unpublish_event_log_removes_from_engines(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        event_log = self._make_event_log(is_published=False)

        registry_response = event_log.model_dump(mode="json", by_alias=True)
        registry_response.pop("is_published", None)
        create_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/event_logs/"
        ).mock(return_value=httpx.Response(201, json=registry_response))
        unpublish_mock = respx_mock.post(
            "http://localhost:8000/api/v1/engines/unpublish"
        ).mock(return_value=httpx.Response(200, json={}))

        registry_client = RegistryClient(api_client=api_client)
        [updated] = registry_client.create_or_update([event_log])

        assert create_mock.called
        request_content = json.loads(create_mock.calls[0].request.content)
        assert "is_published" not in request_content
        assert unpublish_mock.called
        unpublish_content = json.loads(unpublish_mock.calls[0].request.content)
        assert unpublish_content["event_logs"] == [{"name": "my_event_log"}]
        assert updated.is_published is False

    def test_delete_event_log(self, respx_mock: MockRouter, api_client: ApiClient):
        event_log = self._make_event_log(is_published=False)

        delete_mock = respx_mock.delete(
            "http://localhost:8000/api/v1/registry/event_logs/my_event_log"
        ).mock(return_value=httpx.Response(200, json={}))

        registry_client = RegistryClient(api_client=api_client)
        registry_client.delete([event_log])

        assert delete_mock.called

    def test_get_event_log_definition(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        api_response = {
            "name": "my_event_log",
            "version": 1,
            "attribute_key": {"name": "domain_sessionid"},
            "events": [
                {
                    "event": {
                        "name": "page_view",
                        "vendor": "com.snowplowanalytics.snowplow",
                        "version": "1-0-0",
                    },
                    "properties": [{"type": "atomic", "name": "page_url"}],
                }
            ],
            "max_events": 10,
            "max_age_seconds": 600,
            "is_published": True,
            "has_published_version": True,
        }

        get_mock = respx_mock.get(
            "http://localhost:8000/api/v1/registry/event_logs/my_event_log"
        ).mock(return_value=httpx.Response(200, json=api_response))

        registry_client = RegistryClient(api_client=api_client)
        response = registry_client.get_event_log("my_event_log")

        assert get_mock.called
        assert response.name == "my_event_log"
        assert response.is_published is True
        assert response.max_events == 10

    def test_delete_intervention(self, respx_mock: MockRouter, api_client: ApiClient):
        from snowplow_signals.models import (
            InterventionCriterion,
            LinkAttributeKey,
            RuleIntervention,
        )

        intervention = RuleIntervention(
            name="my_intervention",
            owner="test@example.com",
            criteria=InterventionCriterion(
                attribute="my_attribute_group:my_attribute",
                operator=">",
                value=5,
            ),
            target_attribute_keys=[LinkAttributeKey(name="user")],
        )

        delete_mock = respx_mock.delete(
            "http://localhost:8000/api/v1/registry/interventions/my_intervention/versions/1"
        ).mock(return_value=httpx.Response(200, json={}))

        registry_client = RegistryClient(api_client=api_client)
        registry_client.delete([intervention])

        assert delete_mock.called
