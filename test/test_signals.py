import json

import httpx
from respx import MockRouter

from snowplow_signals import (
    AttributeGroup,
    AttributeKey,
    Service,
    Signals,
    domain_userid,
)


class TestSignalsPublish:
    def test_publish_view_and_service(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        view = AttributeGroup(
            name="my_view",
            attribute_key=domain_userid,
            owner="test@example.com",
        )
        service = Service(
            name="my_service",
            views=[view],
            owner="test@example.com",
        )

        # Verify that publish() sets is_published=True in the request
        def check_view_request(request):
            body = json.loads(request.content)
            assert body["is_published"] is True
            # Return a view with is_published=True to verify end-to-end behavior
            return httpx.Response(
                200,
                json={
                    "name": "my_view",
                    "attribute_key": {"name": "user"},
                    "owner": "test@example.com",
                    "is_published": True,
                },
            )

        def check_service_request(request):
            body = json.loads(request.content)
            assert body["is_published"] is True
            return httpx.Response(
                200,
                json={
                    "name": "my_service",
                    "views": [{"name": "my_view"}],
                    "owner": "test@example.com",
                    "is_published": True,
                },
            )

        view_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/attribute_groups/"
        ).mock(side_effect=check_view_request)

        service_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/services/"
        ).mock(side_effect=check_service_request)

        applied_objects = signals_client.publish(objects=[view, service])

        assert view_mock.called
        assert service_mock.called
        assert len(applied_objects) == 2
        assert applied_objects[0].is_published
        assert applied_objects[1].is_published

    def test_publish_entity_view_and_service(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        custom_entity = AttributeKey(
            name="custom_entity",
        )
        view = AttributeGroup(
            name="my_view",
            attribute_key=custom_entity,
            owner="contact@mail.com",
        )
        service = Service(
            name="my_service",
            views=[view],
            owner="contact@mail.com",
        )

        # Verify all requests have is_published=True
        def check_entity_request(request):
            body = json.loads(request.content)
            assert body["is_published"] is True
            return httpx.Response(
                200,
                json={
                    "name": "custom_entity",
                    "is_published": True,
                },
            )

        def check_view_request(request):
            body = json.loads(request.content)
            assert body["is_published"] is True
            return httpx.Response(
                200,
                json={
                    "name": "my_view",
                    "attribute_key": {"name": "custom_entity"},
                    "owner": "contact@mail.com",
                    "is_published": True,
                },
            )

        def check_service_request(request):
            body = json.loads(request.content)
            assert body["is_published"] is True
            return httpx.Response(
                200,
                json={
                    "name": "my_service",
                    "views": [{"name": "my_view"}],
                    "owner": "contact@mail.com",
                    "is_published": True,
                },
            )

        entity_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/attribute_keys/"
        ).mock(side_effect=check_entity_request)

        view_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/attribute_groups/"
        ).mock(side_effect=check_view_request)

        service_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/services/"
        ).mock(side_effect=check_service_request)

        applied_objects = signals_client.publish(objects=[view, service, custom_entity])

        assert entity_mock.called
        assert view_mock.called
        assert service_mock.called
        assert len(applied_objects) == 3
        assert all(obj.is_published for obj in applied_objects)

    def test_already_existing_view(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        view = AttributeGroup(
            name="my_view",
            attribute_key=domain_userid,
            owner="test@example.com",
        )

        def check_publish_flag(request):
            body = json.loads(request.content)
            assert body["is_published"] is True
            return httpx.Response(
                200,
                json={
                    "name": "my_view",
                    "attribute_key": {"name": "user"},
                    "owner": "test@example.com",
                    "is_published": True,
                },
            )

        view_post_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/attribute_groups/"
        ).mock(return_value=httpx.Response(400, json={}))

        view_put_mock = respx_mock.put(
            "http://localhost:8000/api/v1/registry/attribute_groups/my_view/versions/1"
        ).mock(side_effect=check_publish_flag)

        signals_client.publish(objects=[view])

        assert view_post_mock.called
        assert view_put_mock.called


class TestSignalsUnpublish:
    def test_unpublish_view_and_service(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        view = AttributeGroup(
            name="my_view",
            attribute_key=domain_userid,
            owner="test@example.com",
            is_published=True,  # Start as published
        )
        service = Service(
            name="my_service",
            views=[view],
            owner="test@example.com",
            is_published=True,  # Start as published
        )

        # Verify that unpublish() sets is_published=False in the request
        def check_view_request(request):
            body = json.loads(request.content)
            assert body["is_published"] is False
            return httpx.Response(
                200,
                json={
                    "name": "my_view",
                    "attribute_key": {"name": "user"},
                    "owner": "test@example.com",
                    "is_published": False,
                },
            )

        def check_service_request(request):
            body = json.loads(request.content)
            assert body["is_published"] is False
            return httpx.Response(
                200,
                json={
                    "name": "my_service",
                    "views": [{"name": "my_view"}],
                    "owner": "test@example.com",
                    "is_published": False,
                },
            )

        view_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/attribute_groups/"
        ).mock(side_effect=check_view_request)

        service_mock = respx_mock.post(
            "http://localhost:8000/api/v1/registry/services/"
        ).mock(side_effect=check_service_request)

        unpublished_objects = signals_client.unpublish(objects=[view, service])

        assert view_mock.called
        assert service_mock.called
        assert len(unpublished_objects) == 2
        assert not unpublished_objects[0].is_published
        assert not unpublished_objects[1].is_published


class TestSignalsDelete:
    def test_delete_view_and_service(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        view = AttributeGroup(
            name="my_view",
            attribute_key=domain_userid,
            owner="test@example.com",
        )
        service = Service(
            name="my_service",
            views=[view],
            owner="test@example.com",
        )

        view_delete_mock = respx_mock.delete(
            "http://localhost:8000/api/v1/registry/attribute_groups/my_view/versions/1"
        ).mock(return_value=httpx.Response(200, json={}))

        service_delete_mock = respx_mock.delete(
            "http://localhost:8000/api/v1/registry/services/my_service"
        ).mock(return_value=httpx.Response(200, json={}))

        result = signals_client.delete(objects=[view, service])

        assert view_delete_mock.called
        assert service_delete_mock.called
        assert result is None


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
            json__attribute_keys={"domain_userid": ["user-123"]},
        ).mock(return_value=httpx.Response(200, json=api_response))

        response = signals_client.get_service_attributes(
            name="my_service", attribute_key="domain_userid", identifier="user-123"
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
            json__attribute_keys={"domain_userid": ["user-123"]},
            json__attributes=["my_view_v1:page_views_count"],
        ).mock(return_value=httpx.Response(200, json=api_response))

        response = signals_client.get_view_attributes(
            name="my_view",
            version=1,
            attributes=["page_views_count"],
            attribute_key="domain_userid",
            identifier="user-123",
        )
        assert response["domain_userid"] == "user-123"
        assert response["page_views_count"] == 10
