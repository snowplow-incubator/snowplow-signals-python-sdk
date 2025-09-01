from unittest.mock import patch

import httpx
import pytest
from respx import MockRouter

from snowplow_signals import Signals
from snowplow_signals.batch_autogen.models.dbt_project_setup import DbtProjectSetup

from .utils import get_attribute_view_response


def test_batch_setup_get_attribute_views_uses_all_views(
    signals_client: Signals, respx_mock: MockRouter
):
    mock_attribute_views_response = get_attribute_view_response()
    attribute_views_mock = respx_mock.get(
        "http://localhost:8000/api/v1/registry/attribute_groups/"
    ).mock(return_value=httpx.Response(200, json=mock_attribute_views_response))

    dbt_project_setup = DbtProjectSetup(signals_client.api_client, "repo")
    valid_attribute_views = dbt_project_setup._get_attribute_views()
    assert len(mock_attribute_views_response) == len(valid_attribute_views)
    assert attribute_views_mock.call_count == 1


def test_batch_setup_get_attribute_views_uses_specified_view_name(
    signals_client: Signals, respx_mock: MockRouter
):
    mock_attribute_views_response = get_attribute_view_response()
    attribute_views_mock = respx_mock.get(
        "http://localhost:8000/api/v1/registry/attribute_groups/"
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


def test_batch_setup_get_attribute_views_throws_on_empty_views(
    signals_client: Signals, respx_mock: MockRouter
):
    mock_attribute_views_response = get_attribute_view_response()
    respx_mock.get("http://localhost:8000/api/v1/registry/attribute_groups/").mock(
        return_value=httpx.Response(200, json=mock_attribute_views_response)
    )

    dbt_project_setup = DbtProjectSetup(
        signals_client.api_client, "repo", view_name="random_name"
    )
    with pytest.raises(
        ValueError, match="No project/attribute group found with name: random_name"
    ):
        dbt_project_setup._get_attribute_views()


def test_setup_all_projects_skips_views_with_no_attributes_and_fields(
    signals_client: Signals, respx_mock: MockRouter
):
    """
    Test that setup_all_projects skips batch views that have no attributes (attributes is None or empty) AND have fields (not None or empty).
    Views with attributes should be processed.
    """

    mock_views = [
        {
            "name": "with_attributes",
            "version": 1,
            "attribute_key": {"name": "user", "key": "user"},
            "attributes": [
                {
                    "name": "attr1",
                    "events": [{"name": "event1"}],
                    "aggregation": "sum",
                    "type": "int32",
                }
            ],
            "fields": [],
            "feast_name": "with_attributes_v1",
            "attribute_key_or_name": "user",
            "attribute_group_or_attribute_key_ttl": None,
            "stream_source_name": None,
            "full_name": "with_attributes_v1",
        },
        {
            "name": "empty_attributes_with_fields",
            "version": 1,
            "attribute_key": {"name": "user", "key": "user"},
            "attributes": [],
            "fields": [{"name": "f1", "type": "int32"}],
            "feast_name": "empty_attributes_with_fields_v1",
            "attribute_key_or_name": "user",
            "attribute_group_or_attribute_key_ttl": None,
            "stream_source_name": None,
            "full_name": "empty_attributes_with_fields_v1",
        },
        {
            "name": "none_attributes_with_fields",
            "version": 1,
            "attribute_key": {"name": "user", "key": "user"},
            "attributes": None,
            "fields": [{"name": "f2", "type": "int32"}],
            "feast_name": "none_attributes_with_fields_v1",
            "attribute_key_or_name": "user",
            "attribute_group_or_attribute_key_ttl": None,
            "stream_source_name": None,
            "full_name": "none_attributes_with_fields_v1",
        },
    ]
    respx_mock.get("http://localhost:8000/api/v1/registry/attribute_groups/").mock(
        return_value=httpx.Response(200, json=mock_views)
    )
    dbt_project_setup = DbtProjectSetup(signals_client.api_client, "repo")
    with patch.object(dbt_project_setup, "create_project_directories") as mock_create:
        dbt_project_setup.setup_all_projects()
        called_projects = [call[0][0] for call in mock_create.call_args_list]
        assert "with_attributes_1" in called_projects
        assert len(called_projects) == 1
