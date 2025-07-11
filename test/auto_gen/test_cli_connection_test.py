"""
Tests for the CLI interface of the dbt model generation tool.
Verifies command-line argument handling and command execution.
"""

from pathlib import Path
from test.utils import MOCK_API_KEY, MOCK_API_KEY_ID, MOCK_API_URL, MOCK_ORG_ID
from typing import Generator, List
from unittest.mock import MagicMock, patch

import httpx
import pytest
import typer

from snowplow_signals.batch_autogen.cli import app


def test_cli_test_connection_succeeds(
    api_params: List[str],
    mock_successful_registry_views: None,
    mock_successful_api_health: None,
    mock_auth: None,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test successful connection to both auth and API services."""
    caplog.clear()
    with caplog.at_level("INFO"):
        with pytest.raises(SystemExit) as exc_info:
            app(["test-connection"] + api_params)

        assert exc_info.value.code == 0

        # Verify logging output
        assert "Testing authentication service..." in caplog.text
        assert "✅ Authentication service is healthy" in caplog.text
        assert "Testing API service..." in caplog.text
        assert "✅ API service is healthy" in caplog.text
        assert "✨ All services are operational!" in caplog.text


def test_cli_test_connection_verbose(
    api_params: List[str],
    mock_successful_registry_views: None,
    mock_successful_api_health: None,
    mock_auth: None,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test connection with verbose output showing additional details."""
    caplog.clear()
    with caplog.at_level("INFO"):
        with pytest.raises(SystemExit) as exc_info:
            app(["test-connection", "--verbose"] + api_params)

        assert exc_info.value.code == 0

        # Verify verbose logging output
        assert "Testing authentication service..." in caplog.text
        assert "✅ Authentication service is healthy" in caplog.text
        assert "Testing API service..." in caplog.text
        assert "✅ API service is healthy" in caplog.text
        assert "✨ All services are operational!" in caplog.text
        assert "Dependencies status:" in caplog.text


def test_cli_test_connection_auth_only(
    api_params: List[str],
    mock_successful_registry_views: None,
    mock_auth: None,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test connection with only authentication check enabled."""
    caplog.clear()
    with caplog.at_level("INFO"):
        with pytest.raises(SystemExit) as exc_info:
            app(["test-connection", "--no-check-api"] + api_params)

        assert exc_info.value.code == 0

        # Verify logging output
        assert "Testing authentication service..." in caplog.text
        assert "✅ Authentication service is healthy" in caplog.text
        assert "Testing API service..." not in caplog.text
        assert "✨ Selected services are operational!" in caplog.text


def test_cli_test_connection_api_only(
    api_params: List[str],
    mock_successful_api_health: None,
    mock_auth: None,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test connection with only API health check enabled."""
    caplog.clear()
    with caplog.at_level("INFO"):
        with pytest.raises(SystemExit) as exc_info:
            app(["test-connection", "--no-check-auth"] + api_params)

        assert exc_info.value.code == 0

        # Verify logging output
        assert "Testing authentication service..." not in caplog.text
        assert "Testing API service..." in caplog.text
        assert "✅ API service is healthy" in caplog.text
        assert "✨ Selected services are operational!" in caplog.text


def test_cli_test_connection_auth_fails(
    api_params: List[str],
    respx_mock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test connection when authentication fails with 401 Unauthorized."""
    caplog.clear()
    with caplog.at_level("INFO"):
        # Mock failed registry views response
        respx_mock.get(f"{MOCK_API_URL}/api/v1/registry/views/").mock(
            return_value=httpx.Response(401, json={"error": "Unauthorized"})
        )

        with pytest.raises(SystemExit) as exc_info:
            app(["test-connection"] + api_params)

        assert exc_info.value.code == 1

        # Verify logging output
        assert "Testing authentication service..." in caplog.text
        assert "❌ Authentication service is not responding" in caplog.text
        assert "Unauthorized" in caplog.text
        assert "Please check your API credentials and network connection" in caplog.text
        assert "⚠️ API service is not operational" in caplog.text


def test_cli_test_connection_fails_with_down_status(
    api_params: List[str],
    mock_successful_registry_views: None,
    respx_mock,
    mock_auth: None,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test connection when API service reports down status."""
    caplog.clear()
    with caplog.at_level("INFO"):
        # Mock failed health check response
        respx_mock.get(f"{MOCK_API_URL}/health-all").mock(
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

        # Verify logging output
        assert "Testing authentication service..." in caplog.text
        assert "✅ Authentication service is healthy" in caplog.text
        assert "Testing API service..." in caplog.text
        assert "❌ API service is not healthy" in caplog.text
        assert "⚠️ Some services are not operational" in caplog.text


def test_cli_test_connection_fails_with_exception(
    api_params: List[str],
    respx_mock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test connection when auth endpoint is unreachable."""
    caplog.clear()
    with caplog.at_level("INFO"):
        # Mock connection error for auth endpoint
        respx_mock.get(f"{MOCK_API_URL}/api/v1/registry/views/").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        with pytest.raises(SystemExit) as exc_info:
            app(["test-connection"] + api_params)

        assert exc_info.value.code == 1

        # Verify logging output
        assert "Testing authentication service..." in caplog.text
        assert "❌ Authentication service is not responding" in caplog.text
        assert "Connection refused" in caplog.text
        assert "Please check your API credentials and network connection" in caplog.text
        assert "⚠️ API service is not operational" in caplog.text


def test_cli_test_connection_fails_with_non_200_status(
    api_params: List[str],
    respx_mock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test connection when API health check returns 500 error."""
    caplog.clear()
    with caplog.at_level("INFO"):
        # Mock successful auth check
        respx_mock.get(f"{MOCK_API_URL}/api/v1/registry/views/").mock(
            return_value=httpx.Response(200, json={"data": []})
        )
        # Mock non-200 health check response
        respx_mock.get(f"{MOCK_API_URL}/health-all").mock(
            return_value=httpx.Response(500, json={"error": "Internal Server Error"})
        )

        with pytest.raises(SystemExit) as exc_info:
            app(["test-connection"] + api_params)

        assert exc_info.value.code == 1

        # Verify logging output
        assert "Testing authentication service..." in caplog.text
        assert "✅ Authentication service is healthy" in caplog.text
        assert "Testing API service..." in caplog.text
        assert (
            "❌ API service error (HTTP 500): {'error': 'Internal Server Error'}"
            in caplog.text
        )
        assert "⚠️ API service is not operational" in caplog.text
