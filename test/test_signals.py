import httpx
from respx import MockRouter

from snowplow_signals import Entity, LinkEntity, Service, Signals, View, domain_userid
from snowplow_signals.models import ViewResponse


class TestSignalsApply:
    def test_apply_view_and_service(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        view = View(
            name="my_view",
            entity=domain_userid,
            owner="test@example.com",
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
        service = Service(
            name="my_service",
            views=[view],
            owner="test@example.com",
        )

        view_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/views/"
        ).mock(return_value=httpx.Response(201, json=view_output.model_dump()))

        service_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/services/"
        ).mock(return_value=httpx.Response(201, json=service.model_dump()))

        apply_mock = respx_mock.post(
            "http://localhost:8000/api/v1/feature_store/apply"
        ).mock(return_value=httpx.Response(200, json={}))

        applied_objects = signals_client.apply(objects=[view, service])

        assert view_mock.called
        assert service_mock.called
        assert apply_mock.called

        assert len(applied_objects) == 2
        assert applied_objects[0].name == "my_view"
        assert applied_objects[1].name == "my_service"

    def test_apply_entity_view_and_service(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        custom_entity = Entity(
            name="custom_entity",
        )
        view = View(
            name="my_view",
            entity=custom_entity,
            owner="contact@mail.com",
        )
        view_output = ViewResponse(
            name="my_view",
            entity=LinkEntity(name="custom_entity"),
            feast_name="my_view_v1",
            offline=True,
            stream_source_name="my_stream",
            entity_key="user_id",
            view_or_entity_ttl=None,
            owner="contact@mail.com",
        )
        service = Service(
            name="my_service",
            views=[view],
            owner="contact@mail.com",
        )

        entity_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/entities/"
        ).mock(return_value=httpx.Response(201, json=custom_entity.model_dump()))

        view_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/views/"
        ).mock(return_value=httpx.Response(201, json=view_output.model_dump()))

        service_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/services/"
        ).mock(return_value=httpx.Response(201, json=service.model_dump()))

        apply_mock = respx_mock.post(
            "http://localhost:8000/api/v1/feature_store/apply"
        ).mock(return_value=httpx.Response(200, json={}))

        applied_objects = signals_client.apply(objects=[view, service, custom_entity])

        assert entity_mock.called
        assert view_mock.called
        assert service_mock.called
        assert apply_mock.called

        assert len(applied_objects) == 3
        assert applied_objects[0].name == "custom_entity"
        assert applied_objects[1].name == "my_view"
        assert applied_objects[2].name == "my_service"

    def test_already_existing_view(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        view = View(
            name="my_view",
            entity=domain_userid,
            owner="test@example.com",
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

        view_post_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/views/"
        ).mock(return_value=httpx.Response(400, json={}))

        view_get_mock = respx_mock.put(
            "http://localhost:8000/api/v1/registry/views/my_view/versions/1"
        ).mock(return_value=httpx.Response(200, json=view_output.model_dump()))

        apply_mock = respx_mock.post(
            "http://localhost:8000/api/v1/feature_store/apply"
        ).mock(return_value=httpx.Response(200, json={}))

        signals_client.apply(objects=[view])

        assert view_post_mock.called
        assert view_get_mock.called
        assert apply_mock.called


class TestSignalsGetAttributes:
    def test_get_service_attributes(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        api_response = {
            "domain_userid": ["user-123"],
            "page_views_count": [10],
        }
        respx_mock.post(
            "http://localhost:8000/api/v1/get-online-attributes",
            json__service="my_service",
            json__entities={"domain_userid": ["user-123"]},
        ).mock(return_value=httpx.Response(200, json=api_response))

        response = signals_client.get_service_attributes(
            name="my_service", entity="domain_userid", identifier="user-123"
        )

        assert response["domain_userid"] == "user-123"
        assert response["page_views_count"] == 10

    def test_get_view_attributes(self, respx_mock: MockRouter, signals_client: Signals):
        api_response = {
            "domain_userid": ["user-123"],
            "page_views_count": [10],
        }
        respx_mock.post(
            "http://localhost:8000/api/v1/get-online-attributes",
            json__entities={"domain_userid": ["user-123"]},
            json__attributes=["my_view_v1:page_views_count"],
        ).mock(return_value=httpx.Response(200, json=api_response))

        response = signals_client.get_view_attributes(
            name="my_view",
            version=1,
            attributes=["page_views_count"],
            entity="domain_userid",
            identifier="user-123",
        )

        assert response["domain_userid"] == "user-123"
        assert response["page_views_count"] == 10
