"""Tests for the BatchAutogenClient class"""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

from snowplow_signals.api_client import ApiClient
from snowplow_signals.batch_autogen.dbt_client import BatchAutogenClient
from snowplow_signals.batch_autogen.models.dbt_config_generator import (
    DbtConfig,
    FilteredEvents,
    ConfigEvents,
    DailyAggregations,
    ConfigAttributes,
)


@pytest.fixture
def mock_api_client():
    """Create a mock API client"""
    return MagicMock(spec=ApiClient)


@pytest.fixture
def dbt_client(mock_api_client):
    """Create a BatchAutogenClient instance with mocked API client"""
    return BatchAutogenClient(mock_api_client)


@pytest.fixture
def temp_repo_path(tmp_path):
    """Create a temporary repository path"""
    return str(tmp_path)


@pytest.fixture
def mock_project_setup():
    """Mock the DbtProjectSetup class"""
    with patch("snowplow_signals.batch_autogen.dbt_client.DbtProjectSetup") as mock:
        instance = mock.return_value
        instance.setup_all_projects.return_value = True
        yield mock


@pytest.fixture
def mock_dbt_config_generator():
    """Mock the DbtConfigGenerator class"""
    with patch("snowplow_signals.batch_autogen.dbt_client.DbtConfigGenerator") as mock:
        instance = mock.return_value
        mock_config = DbtConfig(
            filtered_events=FilteredEvents(
                events=[ConfigEvents(
                    event_vendor="test",
                    event_name="test",
                    event_format="test",
                    event_version="test"
                )],
                properties=[]
            ),
            daily_agg=DailyAggregations(
                daily_aggregate_attributes=[],
                daily_first_value_attributes=[],
                daily_last_value_attributes=[]
            ),
            attributes=ConfigAttributes(
                lifetime_aggregates=[],
                last_n_day_aggregates=[],
                first_value_attributes=[],
                last_value_attributes=[]
            )
        )
        instance.create_dbt_config.return_value = mock_config
        yield mock


@pytest.fixture
def mock_dbt_asset_generator():
    """Mock the DbtAssetGenerator class"""
    with patch("snowplow_signals.batch_autogen.dbt_client.DbtAssetGenerator") as mock:
        instance = mock.return_value
        instance.generate_asset.return_value = True
        yield mock


def test_init_project_success(dbt_client, temp_repo_path, mock_project_setup):
    """Test successful project initialization"""
    result = dbt_client.init_project(temp_repo_path)
    assert result is True
    mock_project_setup.assert_called_once()


def test_init_project_with_view_name(dbt_client, temp_repo_path, mock_project_setup):
    """Test project initialization with specific view name"""
    result = dbt_client.init_project(temp_repo_path, view_name="test_view")
    assert result is True
    mock_project_setup.assert_called_once_with(
        api_client=dbt_client.api_client,
        repo_path=temp_repo_path,
        view_name="test_view",
        view_version=None,
    )


def test_init_project_with_view_version(dbt_client, temp_repo_path, mock_project_setup):
    """Test project initialization with specific view version"""
    result = dbt_client.init_project(
        temp_repo_path, view_name="test_view", view_version=1
    )
    assert result is True
    mock_project_setup.assert_called_once_with(
        api_client=dbt_client.api_client,
        repo_path=temp_repo_path,
        view_name="test_view",
        view_version=1,
    )


def test_generate_models_single_project_success(
    dbt_client, temp_repo_path, mock_dbt_config_generator, mock_dbt_asset_generator
):
    """Test successful model generation for a single project"""
    # Create project structure
    project_name = "test_project"
    project_path = os.path.join(temp_repo_path, project_name)
    os.makedirs(os.path.join(project_path, "configs"), exist_ok=True)

    # Create base config file
    with open(os.path.join(project_path, "configs", "base_config.json"), "w") as f:
        json.dump({
            "events": [],
            "properties": [],
            "periods": [],
            "transformed_attributes": []
        }, f)

    result = dbt_client.generate_models(temp_repo_path, project_name=project_name)
    assert result is True


def test_generate_models_single_project_not_found(dbt_client, temp_repo_path):
    """Test model generation for non-existent project"""
    result = dbt_client.generate_models(temp_repo_path, project_name="non_existent")
    assert result is False


def test_generate_models_all_projects_success(
    dbt_client, temp_repo_path, mock_dbt_config_generator, mock_dbt_asset_generator
):
    """Test successful model generation for all projects"""
    # Create multiple project structures
    projects = ["project1", "project2"]
    for project in projects:
        project_path = os.path.join(temp_repo_path, project)
        os.makedirs(os.path.join(project_path, "configs"), exist_ok=True)
        with open(os.path.join(project_path, "configs", "base_config.json"), "w") as f:
            json.dump({
                "events": [],
                "properties": [],
                "periods": [],
                "transformed_attributes": []
            }, f)

    result = dbt_client.generate_models(temp_repo_path)
    assert result is True


def test_generate_models_no_projects_found(dbt_client, temp_repo_path):
    """Test model generation when no projects are found"""
    result = dbt_client.generate_models(temp_repo_path)
    assert result is False


def test_generate_models_with_update_flag(
    dbt_client, temp_repo_path, mock_dbt_config_generator, mock_dbt_asset_generator
):
    """Test model generation with update flag"""
    project_name = "test_project"
    project_path = os.path.join(temp_repo_path, project_name)
    os.makedirs(os.path.join(project_path, "configs"), exist_ok=True)

    with open(os.path.join(project_path, "configs", "base_config.json"), "w") as f:
        json.dump({
            "events": [],
            "properties": [],
            "periods": [],
            "transformed_attributes": []
        }, f)

    result = dbt_client.generate_models(
        temp_repo_path, project_name=project_name, update=True
    )
    assert result is True
    # Verify that generate_asset was called with update=True
    mock_dbt_asset_generator.return_value.generate_asset.assert_called_with(
        update=True, context=mock_dbt_asset_generator.return_value.custom_context
    )
