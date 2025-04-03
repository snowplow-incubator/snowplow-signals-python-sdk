"""
End-to-end tests for batch model generation functionality.
These tests verify the complete flow of creating and generating dbt models.
"""

from pathlib import Path

import httpx

from snowplow_signals.dbt.dbt_client import DbtClient

from .utils import get_attribute_view_response_from_file

# Constants
TEST_REPO_PATH = Path("integration_tests/customer_repo")
TEST_VIEW_NAME = "ecommerce_transaction_interactions_features"
TEST_PROJECT_NAME = "ecommerce_transaction_interactions_features_1"
API_ENDPOINT = "http://localhost:8000/api/v1/registry/views/"


def test_batch_model_generation_creates_project_structure(signals_client, respx_mock):
    """
    Test batch model generation by creating and validating a dbt project structure.

    This test:
    1. Creates a new dbt project in integration_tests/customer_repo
    2. Generates models based on a mock attribute view response
    3. Verifies the generated project structure and models
    4. Preserves generated files for manual inspection and dbt command testing

    This test serves as the first step in the integration test suite,
    generating the dbt project that subsequent integration tests will use
    to validate the full model generation and execution workflow.
    """
    # Setup mock response
    mock_attribute_views_response = get_attribute_view_response_from_file()
    respx_mock.get(API_ENDPOINT).mock(
        return_value=httpx.Response(200, json=mock_attribute_views_response)
    )

    # Initialize and generate models
    dbt_client = DbtClient(signals_client.api_client)
    dbt_client.init_project(repo_path=str(TEST_REPO_PATH), view_name=TEST_VIEW_NAME)

    dbt_client.generate_models(
        repo_path=str(TEST_REPO_PATH), project_name=TEST_PROJECT_NAME
    )

    # Verify project structure
    models_path = TEST_REPO_PATH / TEST_PROJECT_NAME / "models"
    assert models_path.exists(), f"Models directory not created at {models_path}"
