"""Tests for the BatchAutogenClient class"""

import json
import os
from typing import Generator, cast
from unittest.mock import MagicMock, patch

import httpx
import pytest
from respx import MockRouter

from snowplow_signals.api_client import ApiClient
from snowplow_signals.batch_autogen.cli_params import (
    TargetType,
)
from snowplow_signals.batch_autogen.dbt_client import BatchAutogenClient
from snowplow_signals.batch_autogen.models.dbt_asset_generator import DbtAssetGenerator
from snowplow_signals.batch_autogen.models.dbt_config_generator import (
    ConfigAttributes,
    ConfigEvents,
    DailyAggregations,
    DbtConfig,
    FilteredEvents,
)


@pytest.fixture
def mock_api_client() -> MagicMock:
    """Create a mock API client"""
    return MagicMock(spec=ApiClient)


@pytest.fixture
def dbt_client(mock_api_client) -> BatchAutogenClient:
    """Create a BatchAutogenClient instance with mocked API client"""
    return BatchAutogenClient(mock_api_client, target_type="snowflake")


@pytest.fixture
def temp_repo_path(tmp_path) -> str:
    """Create a temporary repository path"""
    return str(tmp_path)


@pytest.fixture
def mock_project_setup() -> Generator[MagicMock, None, None]:
    """Mock the DbtProjectSetup class"""
    with patch("snowplow_signals.batch_autogen.dbt_client.DbtProjectSetup") as mock:
        instance = mock.return_value
        instance.setup_all_projects.return_value = True
        yield mock


@pytest.fixture
def mock_dbt_config_generator() -> Generator[MagicMock, None, None]:
    """Mock the DbtConfigGenerator class"""
    with patch("snowplow_signals.batch_autogen.dbt_client.DbtConfigGenerator") as mock:
        instance = mock.return_value
        mock_config = DbtConfig(
            filtered_events=FilteredEvents(
                events=[
                    ConfigEvents(
                        event_vendor="test",
                        event_name="test",
                        event_format="test",
                        event_version="test",
                    )
                ],
                properties=[],
            ),
            daily_agg=DailyAggregations(
                daily_aggregate_attributes=[],
                daily_first_value_attributes=[],
                daily_last_value_attributes=[],
            ),
            attributes=ConfigAttributes(
                lifetime_aggregates=[],
                last_n_day_aggregates=[],
                first_value_attributes=[],
                last_value_attributes=[],
                unique_list_attributes=[],
            ),
        )
        instance.create_dbt_config.return_value = mock_config
        yield mock


@pytest.fixture
def mock_dbt_asset_generator() -> Generator[MagicMock, None, None]:
    """Mock the DbtAssetGenerator class"""
    with patch("snowplow_signals.batch_autogen.dbt_client.DbtAssetGenerator") as mock:
        instance = mock.return_value
        instance.generate_asset.return_value = True
        yield mock


def test_init_project_success(
    dbt_client: BatchAutogenClient, temp_repo_path: str, mock_project_setup: MagicMock
):
    """Test successful project initialization"""
    result = dbt_client.init_project(temp_repo_path)
    assert result is True
    mock_project_setup.assert_called_once()


def test_init_project_with_attribute_group_name(
    dbt_client: BatchAutogenClient, temp_repo_path: str, mock_project_setup: MagicMock
):
    """Test project initialization with specific view name"""
    result = dbt_client.init_project(temp_repo_path, attribute_group_name="test_view")
    assert result is True
    mock_project_setup.assert_called_once_with(
        api_client=dbt_client.api_client,
        repo_path=temp_repo_path,
        attribute_group_name="test_view",
        attribute_group_version=None,
        target_type=TargetType.snowflake,
    )


def test_init_project_with_attribute_group_version(
    dbt_client: BatchAutogenClient, temp_repo_path: str, mock_project_setup: MagicMock
):
    """Test project initialization with specific view version"""
    result = dbt_client.init_project(
        temp_repo_path, attribute_group_name="test_view", attribute_group_version=1
    )
    assert result is True
    mock_project_setup.assert_called_once_with(
        api_client=dbt_client.api_client,
        repo_path=temp_repo_path,
        attribute_group_name="test_view",
        attribute_group_version=1,
        target_type=TargetType.snowflake,
    )


@pytest.mark.usefixtures("mock_dbt_config_generator", "mock_dbt_asset_generator")
def test_generate_models_single_project_success(
    dbt_client: BatchAutogenClient, temp_repo_path: str
):
    """Test successful model generation for a single project"""
    # Create project structure
    project_name = "test_project"
    project_path = os.path.join(temp_repo_path, project_name)
    os.makedirs(os.path.join(project_path, "configs"), exist_ok=True)

    # Create base config file
    with open(os.path.join(project_path, "configs", "base_config.json"), "w") as f:
        json.dump(
            {
                "events": [],
                "properties": [],
                "periods": [],
                "transformed_attributes": [],
                "attribute_key": "user_id",
            },
            f,
        )

    result = dbt_client.generate_models(temp_repo_path, project_name=project_name)
    assert result is True


def test_generate_models_single_project_not_found(
    dbt_client: BatchAutogenClient, temp_repo_path: str
):
    """Test model generation for non-existent project"""
    result = dbt_client.generate_models(temp_repo_path, project_name="non_existent")
    assert result is False


@pytest.mark.usefixtures("mock_dbt_config_generator", "mock_dbt_asset_generator")
def test_generate_models_all_projects_success(
    dbt_client: BatchAutogenClient, temp_repo_path: str
):
    """Test successful model generation for all projects"""
    # Create multiple project structures
    projects = ["project1", "project2"]
    for project in projects:
        project_path = os.path.join(temp_repo_path, project)
        os.makedirs(os.path.join(project_path, "configs"), exist_ok=True)
        with open(os.path.join(project_path, "configs", "base_config.json"), "w") as f:
            json.dump(
                {
                    "events": [],
                    "properties": [],
                    "periods": [],
                    "transformed_attributes": [],
                    "attribute_key": "user_id",
                },
                f,
            )

    result = dbt_client.generate_models(temp_repo_path)
    assert result is True


def test_generate_models_no_projects_found(
    dbt_client: BatchAutogenClient, temp_repo_path: str
):
    """Test model generation when no projects are found"""
    result = dbt_client.generate_models(temp_repo_path)
    assert result is False


@pytest.mark.usefixtures("mock_dbt_config_generator")
def test_generate_models_with_update_flag(
    dbt_client: BatchAutogenClient,
    temp_repo_path: str,
    mock_dbt_asset_generator: MagicMock,
):
    """Test model generation with update flag"""
    project_name = "test_project"
    project_path = os.path.join(temp_repo_path, project_name)
    os.makedirs(os.path.join(project_path, "configs"), exist_ok=True)

    with open(os.path.join(project_path, "configs", "base_config.json"), "w") as f:
        json.dump(
            {
                "events": [],
                "properties": [],
                "periods": [],
                "transformed_attributes": [],
                "attribute_key": "user_id",
            },
            f,
        )

    result = dbt_client.generate_models(
        temp_repo_path, project_name=project_name, update=True
    )
    assert result is True
    # Verify that generate_asset was called with update=True
    cast(
        MagicMock,
        cast(DbtAssetGenerator, mock_dbt_asset_generator.return_value).generate_asset,
    ).assert_called_with(
        update=True,
        context=cast(
            DbtAssetGenerator, mock_dbt_asset_generator.return_value
        ).custom_context,
    )


def test_sync_model_api_requests(
    api_client: ApiClient, temp_repo_path: str, respx_mock: MockRouter
):
    """Test successful model synchronization with correct HTTP requests"""
    attribute_group_name = "test_view"
    attribute_group_version = 1
    project_name = f"{attribute_group_name}_{attribute_group_version}"
    project_path = os.path.join(temp_repo_path, project_name)
    configs_path = os.path.join(project_path, "configs")
    os.makedirs(configs_path, exist_ok=True)

    batch_source_config = {
        "database": "test_database",
        "wh_schema": "test_schema",
        "table": f"{attribute_group_name}_{attribute_group_version}_attributes",
        "name": f"{attribute_group_name}_{attribute_group_version}_attributes",
        "timestamp_field": "valid_at_tstamp",
        "description": f"Table containing attributes for {attribute_group_name}_{attribute_group_version} view",
        "owner": "test@example.com",
    }

    with open(os.path.join(configs_path, "batch_source_config.json"), "w") as f:
        json.dump(batch_source_config, f)

    batch_source_mock = respx_mock.put(
        f"http://localhost:8000/api/v1/registry/attribute_groups/{attribute_group_name}/versions/{attribute_group_version}/batch_source"
    ).mock(return_value=httpx.Response(200, json={}))

    publish_mock = respx_mock.post("http://localhost:8000/api/v1/engines/publish").mock(
        return_value=httpx.Response(200, json={"status": "published"})
    )

    dbt_client = BatchAutogenClient(api_client, target_type="snowflake")

    dbt_client.sync_model(
        project_path=project_path,
        attribute_group_name=attribute_group_name,
        attribute_group_version=attribute_group_version,
        verbose=False,
    )

    assert batch_source_mock.called
    batch_source_request = batch_source_mock.calls[0].request
    assert batch_source_request.method == "PUT"

    request_body = json.loads(batch_source_request.content)
    assert request_body["database"] == "test_database"
    assert request_body["wh_schema"] == "test_schema"
    assert (
        request_body["table"]
        == f"{attribute_group_name}_{attribute_group_version}_attributes"
    )
    assert (
        request_body["name"]
        == f"{attribute_group_name}_{attribute_group_version}_attributes"
    )
    assert request_body["timestamp_field"] == "valid_at_tstamp"
    assert (
        request_body["description"]
        == f"Table containing attributes for {attribute_group_name}_{attribute_group_version} view"
    )
    assert request_body["owner"] == "test@example.com"

    assert publish_mock.called
    publish_request = publish_mock.calls[0].request
    assert publish_request.method == "POST"

    publish_body = json.loads(publish_request.content)
    assert "attribute_groups" in publish_body
    assert len(publish_body["attribute_groups"]) == 1
    assert publish_body["attribute_groups"][0]["name"] == attribute_group_name
    assert publish_body["attribute_groups"][0]["version"] == attribute_group_version
