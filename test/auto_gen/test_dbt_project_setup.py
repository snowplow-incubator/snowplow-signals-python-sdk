import httpx
import pytest

from snowplow_signals.dbt.models.dbt_project_setup import DbtProjectSetup

from .utils import get_attribute_view_response


def test_batch_setup_uses_all_views(signals_client, respx_mock):
    mock_attribute_views_response = get_attribute_view_response()
    attribute_views_mock = respx_mock.get(
        "http://localhost:8000/api/v1/registry/views/"
    ).mock(return_value=httpx.Response(200, json=mock_attribute_views_response))

    dbt_project_setup = DbtProjectSetup(signals_client.api_client, "repo")
    valid_attribute_views = dbt_project_setup._get_attribute_views()
    assert len(mock_attribute_views_response) == len(valid_attribute_views)
    assert attribute_views_mock.call_count == 1


def test_batch_setup_uses_specified_view_name(signals_client, respx_mock):
    mock_attribute_views_response = get_attribute_view_response()
    attribute_views_mock = respx_mock.get(
        "http://localhost:8000/api/v1/registry/views/"
    ).mock(return_value=httpx.Response(200, json=mock_attribute_views_response))

    dbt_project_setup = DbtProjectSetup(
        signals_client.api_client,
        "repo",
        view_name=mock_attribute_views_response[0]["name"],
    )
    valid_attribute_views = dbt_project_setup._get_attribute_views()
    assert len(mock_attribute_views_response) == 2
    assert len(valid_attribute_views) == 1
    assert attribute_views_mock.call_count == 1


def test_batch_setup_throws_on_empty_views(signals_client, respx_mock):
    mock_attribute_views_response = get_attribute_view_response()
    respx_mock.get("http://localhost:8000/api/v1/registry/views/").mock(
        return_value=httpx.Response(200, json=mock_attribute_views_response)
    )

    dbt_project_setup = DbtProjectSetup(
        signals_client.api_client, "repo", view_name="random_name"
    )
    with pytest.raises(
        ValueError, match="No project/attribute view found with name: random_name"
    ):
        dbt_project_setup._get_attribute_views()
