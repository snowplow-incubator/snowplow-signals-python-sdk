"""
Tests for verifying the output of generated files.
"""

from pathlib import Path

import httpx
import pytest
from respx import MockRouter
from syrupy.assertion import SnapshotAssertion

from snowplow_signals import Signals
from snowplow_signals.batch_autogen.dbt_client import BatchAutogenClient

from .utils import get_integration_test_view_response

# Test constants
TEST_ATTRIBUTE_GROUP_NAME = "ecommerce_transaction_interactions_features"
TEST_PROJECT_NAME = "ecommerce_transaction_interactions_features_1"
API_ENDPOINT = "http://localhost:8000/api/v1/registry/attribute_groups/"


def get_file_contents(directory: Path) -> dict:
    """Get contents of all files in a directory."""
    contents = {}
    for path in directory.rglob("*"):
        if path.is_file():
            try:
                contents[str(path.relative_to(directory))] = path.read_text()
            except UnicodeDecodeError:
                continue
    return contents


@pytest.fixture
def test_dir(tmp_path) -> Path:
    """Create a temporary directory for the test."""
    return tmp_path


def test_generated_files_bigquery(
    test_dir: Path,
    signals_client: Signals,
    respx_mock: MockRouter,
    snapshot: SnapshotAssertion,
):
    """Test that the generated files are correct."""
    # Setup mock API response
    mock_response = get_integration_test_view_response(warehouse="bigquery")
    respx_mock.get(API_ENDPOINT).mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    # Generate the files
    client = BatchAutogenClient(signals_client.api_client, target_type="bigquery")
    client.init_project(
        repo_path=str(test_dir), attribute_group_name=TEST_ATTRIBUTE_GROUP_NAME
    )
    success = client.generate_models(
        repo_path=str(test_dir), project_name=TEST_PROJECT_NAME
    )
    assert success, "Model generation failed, see logs with `-s`"
    # Compare generated files with snapshot
    actual_files = get_file_contents(test_dir)
    assert actual_files == snapshot
