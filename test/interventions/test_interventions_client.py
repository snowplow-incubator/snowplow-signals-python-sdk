from threading import active_count
from unittest.mock import Mock

import httpx
import pytest
from respx import MockRouter

from snowplow_signals.api_client import ApiClient
from snowplow_signals.interventions_client import InterventionsClient

from .utils import (
    get_example_intervention,
    get_intervention_response,
    get_intervention_stream,
    get_interventions_response,
    get_publishable_intervention,
)


class TestInterventionsClient:
    @pytest.fixture
    def interventions_client(self, api_client: ApiClient) -> InterventionsClient:
        return InterventionsClient(api_client=api_client)

    def test_get_intervention(
        self, respx_mock: MockRouter, interventions_client: InterventionsClient
    ):
        mock_intervention_response = get_intervention_response()
        respx_mock.get(
            f"http://localhost:8000/api/v1/registry/interventions/{mock_intervention_response['name']}"
        ).mock(return_value=httpx.Response(200, json=mock_intervention_response))

        intervention = interventions_client.get(
            name=mock_intervention_response["name"],
        )

        assert intervention.name == mock_intervention_response["name"]
        assert intervention.version == mock_intervention_response["version"]

    def test_get_interventions(
        self, respx_mock: MockRouter, interventions_client: InterventionsClient
    ):
        mock_interventions_response = get_interventions_response()
        respx_mock.get(f"http://localhost:8000/api/v1/registry/interventions/").mock(
            return_value=httpx.Response(200, json=mock_interventions_response)
        )

        intervention = interventions_client.list()
        assert len(intervention) == 2
        assert intervention[0].name == mock_interventions_response[0]["name"]
        assert intervention[1].name == mock_interventions_response[1]["name"]

    def test_create_intervention(
        self, respx_mock: MockRouter, interventions_client: InterventionsClient
    ):
        intervention_instance = get_example_intervention()
        respx_mock.post(f"http://localhost:8000/api/v1/registry/interventions/").mock(
            return_value=httpx.Response(200, json=intervention_instance.model_dump())
        )

        created_intervention = interventions_client.create(
            intervention=intervention_instance
        )
        assert created_intervention.name == intervention_instance.name
        assert created_intervention.version == intervention_instance.version

    def test_push_intervention(
        self, respx_mock: MockRouter, interventions_client: InterventionsClient
    ):
        respx_mock.post("http://localhost:8000/api/v1/interventions").mock(
            httpx.Response(200, json={"status": "undelivered"})
        )

        targets, intervention = get_publishable_intervention()

        delivery_status = interventions_client.publish(intervention, targets)

        assert delivery_status == "undelivered"

    def test_pull_intervention(
        self, respx_mock: MockRouter, interventions_client: InterventionsClient
    ):
        targets, stream_bytes = get_intervention_stream()
        assert targets.root is not None

        respx_mock.get("http://localhost:8000/api/v1/interventions").mock(
            httpx.Response(200, stream=httpx.ByteStream(stream_bytes))
        )

        mock = Mock(return_value=None)
        start_threads = active_count()
        with interventions_client.subscribe(targets) as sub:
            assert active_count() == start_threads + 1
            sub.add_handler(mock)
            some = False
            for intervention in sub:
                some = True
                assert intervention is not None
                assert intervention.target_attribute_key is not None
                assert intervention.target_attribute_key.name in targets.root
                assert (
                    intervention.target_attribute_key.id
                    == targets.root["domain_userid"][0]
                )
                mock.assert_called_once_with(intervention)

            assert some

        assert active_count() == start_threads
