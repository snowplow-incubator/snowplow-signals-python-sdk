import httpx
import pytest

from snowplow_signals.interventions_client import InterventionsClient

from .utils import (
    get_example_intervention,
    get_intervention_response,
    get_interventions_response,
)


class TestInterventionsClient:
    @pytest.fixture
    def interventions_client(self, api_client):
        return InterventionsClient(api_client=api_client)

    def test_get_intervention(self, respx_mock, interventions_client):
        mock_intervention_response = get_intervention_response()
        respx_mock.get(
            f"http://localhost:8000/api/v1/registry/interventions/{mock_intervention_response['name']}"
        ).mock(return_value=httpx.Response(200, json=mock_intervention_response))

        intervention = interventions_client.get(
            name=mock_intervention_response["name"],
        )

        assert intervention.name == mock_intervention_response["name"]
        assert intervention.version == mock_intervention_response["version"]

    def test_get_interventions(self, respx_mock, interventions_client):
        mock_interventions_response = get_interventions_response()
        respx_mock.get(f"http://localhost:8000/api/v1/registry/interventions/").mock(
            return_value=httpx.Response(200, json=mock_interventions_response)
        )

        intervention = interventions_client.list()
        assert len(intervention) == 2
        assert intervention[0].name == mock_interventions_response[0]["name"]
        assert intervention[1].name == mock_interventions_response[1]["name"]

    def test_create_intervention(self, respx_mock, interventions_client):
        intervention_instance = get_example_intervention()
        respx_mock.post(f"http://localhost:8000/api/v1/registry/interventions/").mock(
            return_value=httpx.Response(200, json=intervention_instance.model_dump())
        )

        created_intervention = interventions_client.create(
            intervention=intervention_instance
        )
        assert created_intervention.name == intervention_instance.name
        assert created_intervention.version == intervention_instance.version
