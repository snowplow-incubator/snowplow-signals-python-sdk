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
