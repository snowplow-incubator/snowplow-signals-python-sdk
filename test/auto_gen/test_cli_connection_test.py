"""
Tests for the CLI interface of the dbt model generation tool.
Verifies command-line argument handling and command execution.
"""

from pathlib import Path
from typing import Generator, List
from unittest.mock import MagicMock, patch

import httpx
import pytest
import typer

from snowplow_signals.dbt.cli import app
from test.utils import MOCK_API_KEY, MOCK_API_KEY_ID, MOCK_API_URL, MOCK_ORG_ID


def test_cli_test_connection_succeeds(
    api_params: List[str],
    mock_successful_registry_views: None,
    mock_successful_api_health: None,
    mock_auth: None,
) -> None:
    """
    Test successful API connection check.

    Args:
        api_params: API-related command line arguments
        mock_successful_registry_views: Mock for successful registry views
        mock_successful_api_health: Mock for successful API health
        mock_auth: Mock for authentication
    """
    with pytest.raises(SystemExit) as exc_info:
        app(["test-connection"] + api_params)

    assert exc_info.value.code == 0


def test_cli_test_connection_auth_only(
    api_params: List[str],
    mock_successful_registry_views: None,
    mock_auth: None,
) -> None:
    """
    Test API connection check with only authentication check.

    Args:
        api_params: API-related command line arguments
        mock_successful_registry_views: Mock for successful registry views
        mock_auth: Mock for authentication
    """
    with pytest.raises(SystemExit) as exc_info:
        app(["test-connection", "--no-check-api"] + api_params)

    assert exc_info.value.code == 0


def test_cli_test_connection_api_only(
    api_params: List[str],
    mock_successful_api_health: None,
    mock_auth: None,
) -> None:
    """
    Test API connection check with only API health check.

    Args:
        api_params: API-related command line arguments
        mock_successful_api_health: Mock for successful API health
        mock_auth: Mock for authentication
    """
    with pytest.raises(SystemExit) as exc_info:
        app(["test-connection", "--no-check-auth"] + api_params)

    assert exc_info.value.code == 0


def test_cli_test_connection_auth_fails(
    api_params: List[str],
    respx_mock,
) -> None:
    """
    Test API connection check when authentication fails.

    Args:
        api_params: API-related command line arguments
        respx_mock: HTTPX mock fixture
    """
    # Mock failed registry views response
    respx_mock.get(f"{MOCK_API_URL}/api/v1/registry/views/").mock(
        return_value=httpx.Response(401, json={"error": "Unauthorized"})
    )

    with pytest.raises(SystemExit) as exc_info:
        app(["test-connection"] + api_params)

    assert exc_info.value.code == 1


def test_cli_test_connection_fails_with_down_status(
    api_params: List[str],
    mock_successful_registry_views: None,
    respx_mock,
    mock_auth: None,
) -> None:
    """
    Test API connection check when service is down.

    Args:
        api_params: API-related command line arguments
        mock_successful_registry_views: Mock for successful registry views
        respx_mock: HTTPX mock fixture
        mock_auth: Mock for authentication
    """
    # Mock failed health check response
    respx_mock.get(f"{MOCK_API_URL}/api/v1/health-all").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "down",
                "dependencies": {"storage": "ok", "feature_server": "down"},
            },
        )
    )

    with pytest.raises(SystemExit) as exc_info:
        app(["test-connection"] + api_params)

    assert exc_info.value.code == 1


def test_cli_test_connection_fails_with_exception(
    api_params: List[str],
    respx_mock,
) -> None:
    """
    Test API connection check when an exception occurs.

    Args:
        api_params: API-related command line arguments
        respx_mock: HTTPX mock fixture
    """
    # Mock connection error
    respx_mock.get(f"{MOCK_API_URL}/api/v1/registry/views/").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )

    with pytest.raises(SystemExit) as exc_info:
        app(["test-connection"] + api_params)

    assert exc_info.value.code == 1


def test_cli_test_connection_fails_with_non_200_status(
    api_params: List[str],
    respx_mock,
) -> None:
    """
    Test API connection check when API returns non-200 status code.

    Args:
        api_params: API-related command line arguments
        respx_mock: HTTPX mock fixture
    """
    # Mock non-200 health check response
    respx_mock.get("http://localhost:8087/api/v1/health-all").mock(
        return_value=httpx.Response(500, json={"error": "Internal Server Error"})
    )

    with pytest.raises(SystemExit) as exc_info:
        app(["test-connection"] + api_params)

    assert exc_info.value.code == 1
