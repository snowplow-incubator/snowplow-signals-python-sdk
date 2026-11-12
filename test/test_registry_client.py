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

    def test_updates_snowplow_id_lookup_identifiers(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        from snowplow_signals import AttributeKey

        # snowplow_id is built in, so creating it is refused and the client updates it.
        respx_mock.post("http://localhost:8000/api/v1/registry/attribute_keys/").mock(
            return_value=httpx.Response(400, json={"detail": "already exists"})
        )
        put_mock = respx_mock.put(
            "http://localhost:8000/api/v1/registry/attribute_keys/snowplow_id"
        ).mock(
            side_effect=lambda request: httpx.Response(
                200, json={**json.loads(request.content), "blobl_path": None}
            )
        )

        registry_client = RegistryClient(api_client=api_client)
        registry_client.create_or_update(
            [AttributeKey(name="snowplow_id", lookup_identifiers=["domain_userid"])]
        )

        assert put_mock.called
        body = json.loads(put_mock.calls[0].request.content)
        assert body["key"] == "snowplow_id"
        assert body["property"] == {
            "type": "entity",
            "vendor": "com.snowplowanalytics.snowplow",
            "name": "identity",
            "major_version": 2,
            "path": "snowplow_id",
            "index": 0,
        }
        assert body["lookup_identifiers"] == ["domain_userid"]

    def test_snowplow_id_leaves_lookup_identifiers_out(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        from snowplow_signals import snowplow_id

        respx_mock.post("http://localhost:8000/api/v1/registry/attribute_keys/").mock(
            return_value=httpx.Response(400, json={"detail": "already exists"})
        )
        put_mock = respx_mock.put(
            "http://localhost:8000/api/v1/registry/attribute_keys/snowplow_id"
        ).mock(
            side_effect=lambda request: httpx.Response(
                200, json={**json.loads(request.content), "blobl_path": None}
            )
        )

        registry_client = RegistryClient(api_client=api_client)
        registry_client.create_or_update([snowplow_id])

        # Left out, the API keeps the stored selection; an empty list would clear it.
        assert "lookup_identifiers" not in json.loads(put_mock.calls[0].request.content)

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


class TestAgenticAttributes:
    REGISTRY_URL = "http://localhost:8000/api/v1/registry/agentic_attributes/"

    def _make_agentic_attribute(self, is_published: bool):
        from snowplow_signals import (
            AgenticAttribute,
            CriteriaTrigger,
            TriggerCriterion,
            domain_sessionid,
        )

        return AgenticAttribute(
            name="needs_help",
            attribute_key=domain_sessionid,
            output_type="boolean",
            goal="Does the shopper need help?",
            contexts=["my_event_log"],
            triggers=[
                CriteriaTrigger(
                    criteria=TriggerCriterion(
                        attribute="session_stats:page_views",
                        operator=">",
                        value=3,
                    )
                )
            ],
            is_published=is_published,
        )

    def _registry_response(self, agentic_attribute) -> dict:
        response = agentic_attribute.model_dump(mode="json", exclude_none=True)
        # The registry returns the state of the draft row it just wrote.
        response["is_published"] = False
        response["has_published_version"] = False
        return response

    def _calls(self, respx_mock: MockRouter) -> list[tuple[str, str, dict | None]]:
        return [
            (
                call.request.method,
                call.request.url.path,
                json.loads(call.request.content) if call.request.content else None,
            )
            for call in respx_mock.calls
            if call.request.url.host == "localhost"
        ]

    def test_publish_creates_draft_and_promotes_to_engines(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        agentic_attribute = self._make_agentic_attribute(is_published=True)
        respx_mock.post(self.REGISTRY_URL).mock(
            return_value=httpx.Response(
                200, json=self._registry_response(agentic_attribute)
            )
        )
        respx_mock.post("http://localhost:8000/api/v1/engines/publish").mock(
            return_value=httpx.Response(200, json={"status": "published"})
        )

        registry_client = RegistryClient(api_client=api_client)
        [updated] = registry_client.create_or_update([agentic_attribute])

        [create, publish] = self._calls(respx_mock)
        assert create[:2] == ("POST", "/api/v1/registry/agentic_attributes/")
        assert create[2] is not None
        assert create[2]["contexts"] == ["my_event_log"]
        assert create[2]["attribute_key"] == {"name": "domain_sessionid"}
        assert "is_published" not in create[2]
        assert publish == (
            "POST",
            "/api/v1/engines/publish",
            {"agentic_attributes": [{"name": "needs_help"}]},
        )
        assert updated.is_published is True

    def test_existing_attribute_is_updated(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        agentic_attribute = self._make_agentic_attribute(is_published=True)
        respx_mock.post(self.REGISTRY_URL).mock(
            return_value=httpx.Response(400, json={"detail": "already exists"})
        )
        put_mock = respx_mock.put(f"{self.REGISTRY_URL}needs_help").mock(
            return_value=httpx.Response(
                200, json=self._registry_response(agentic_attribute)
            )
        )
        respx_mock.post("http://localhost:8000/api/v1/engines/publish").mock(
            return_value=httpx.Response(200, json={"status": "published"})
        )

        registry_client = RegistryClient(api_client=api_client)
        registry_client.create_or_update([agentic_attribute])

        assert put_mock.called
        assert "is_published" not in json.loads(put_mock.calls[0].request.content)

    def test_unpublish_removes_from_engines(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        agentic_attribute = self._make_agentic_attribute(is_published=False)
        respx_mock.post(self.REGISTRY_URL).mock(
            return_value=httpx.Response(
                200, json=self._registry_response(agentic_attribute)
            )
        )
        unpublish_mock = respx_mock.post(
            "http://localhost:8000/api/v1/engines/unpublish"
        ).mock(return_value=httpx.Response(200, json={"status": "unpublished"}))

        registry_client = RegistryClient(api_client=api_client)
        [updated] = registry_client.create_or_update([agentic_attribute])

        assert json.loads(unpublish_mock.calls[0].request.content) == {
            "agentic_attributes": [{"name": "needs_help"}]
        }
        assert updated.is_published is False

    def _mock_event_log_and_agentic_attribute(
        self, respx_mock: MockRouter, event_log, agentic_attribute
    ):
        event_log_response = event_log.model_dump(mode="json", by_alias=True)
        event_log_response.pop("is_published", None)
        respx_mock.post("http://localhost:8000/api/v1/registry/event_logs/").mock(
            return_value=httpx.Response(200, json=event_log_response)
        )
        respx_mock.post(self.REGISTRY_URL).mock(
            return_value=httpx.Response(
                200, json=self._registry_response(agentic_attribute)
            )
        )
        respx_mock.post("http://localhost:8000/api/v1/engines/publish").mock(
            return_value=httpx.Response(200, json={"status": "published"})
        )
        respx_mock.post("http://localhost:8000/api/v1/engines/unpublish").mock(
            return_value=httpx.Response(200, json={"status": "unpublished"})
        )

    def test_publishes_event_logs_before_agentic_attributes(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        event_log = TestRegistryClient()._make_event_log(is_published=True)
        agentic_attribute = self._make_agentic_attribute(is_published=True)
        self._mock_event_log_and_agentic_attribute(
            respx_mock, event_log, agentic_attribute
        )

        registry_client = RegistryClient(api_client=api_client)
        registry_client.create_or_update([agentic_attribute, event_log])

        engine_calls = [
            body
            for _, path, body in self._calls(respx_mock)
            if path == "/api/v1/engines/publish"
        ]
        assert engine_calls == [
            {"event_logs": [{"name": "my_event_log"}]},
            {"agentic_attributes": [{"name": "needs_help"}]},
        ]

    def test_unpublishes_agentic_attributes_before_event_logs(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        event_log = TestRegistryClient()._make_event_log(is_published=False)
        agentic_attribute = self._make_agentic_attribute(is_published=False)
        self._mock_event_log_and_agentic_attribute(
            respx_mock, event_log, agentic_attribute
        )

        registry_client = RegistryClient(api_client=api_client)
        registry_client.create_or_update([event_log, agentic_attribute])

        engine_calls = [
            body
            for _, path, body in self._calls(respx_mock)
            if path == "/api/v1/engines/unpublish"
        ]
        assert engine_calls == [
            {"agentic_attributes": [{"name": "needs_help"}]},
            {"event_logs": [{"name": "my_event_log"}]},
        ]

    def test_deletes_agentic_attributes_before_event_logs(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        event_log = TestRegistryClient()._make_event_log(is_published=False)
        agentic_attribute = self._make_agentic_attribute(is_published=False)
        respx_mock.delete(f"{self.REGISTRY_URL}needs_help").mock(
            return_value=httpx.Response(200, json={})
        )
        respx_mock.delete(
            "http://localhost:8000/api/v1/registry/event_logs/my_event_log"
        ).mock(return_value=httpx.Response(200, json={}))

        registry_client = RegistryClient(api_client=api_client)
        registry_client.delete([event_log, agentic_attribute])

        assert [path for _, path, _ in self._calls(respx_mock)] == [
            "/api/v1/registry/agentic_attributes/needs_help",
            "/api/v1/registry/event_logs/my_event_log",
        ]

    def test_get_agentic_attribute_definition(
        self, respx_mock: MockRouter, api_client: ApiClient
    ):
        agentic_attribute = self._make_agentic_attribute(is_published=True)
        api_response = self._registry_response(agentic_attribute)
        api_response["is_published"] = True
        api_response["has_published_version"] = True
        respx_mock.get(f"{self.REGISTRY_URL}needs_help").mock(
            return_value=httpx.Response(200, json=api_response)
        )

        registry_client = RegistryClient(api_client=api_client)
        response = registry_client.get_agentic_attribute("needs_help")

        assert response.name == "needs_help"
        assert response.output_type == "boolean"
        assert response.contexts == ["my_event_log"]
        assert response.is_published is True
