import httpx

from snowplow_signals import LinkEntity, Service, View, domain_userid
from snowplow_signals.models import ViewResponse


class TestSignalsApply:
    def test_apply_view_and_service(self, signals_client, respx_mock):
        view = View(
            name="my_view",
            entity=domain_userid,
        )
        view_output = ViewResponse(
            name="my_view",
            entity=LinkEntity(name="user"),
            feast_name="my_view_v1",
            offline=True,
            stream_source_name="my_stream",
            entity_key="user_id",
            view_or_entity_ttl=None,
        )
        service = Service(
            name="my_service",
            views=[view],
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

    def test_already_existing_view(self, signals_client, respx_mock):
        view = View(
            name="my_view",
            entity=domain_userid,
        )
        view_output = ViewResponse(
            name="my_view",
            entity=LinkEntity(name="user"),
            feast_name="my_view_v1",
            offline=True,
            stream_source_name="my_stream",
            entity_key="user_id",
            view_or_entity_ttl=None,
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
