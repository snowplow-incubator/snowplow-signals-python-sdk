"""
Tests for the CLI interface of the dbt model generation tool.
Verifies command-line argument handling and command execution.
"""

import pytest
import httpx
from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import List

from snowplow_signals.dbt.cli import app

# Constants
TEST_API_URL = "http://localhost:8087"
TEST_API_KEY = "test-api-key"
TEST_API_KEY_ID = "test-key-id"
TEST_ORG_ID = "test-org-id"
TEST_VIEW_NAME = "test_view"
TEST_VIEW_VERSION = 1

@pytest.fixture(scope="session")
def test_repo_dir() -> Path:
    """
    Create a persistent directory for testing.
    
    Returns:
        Path: Path to the test directory
        
    Note:
        The directory is cleaned up after all tests are completed.
    """
    test_dir = Path(__file__).parent / "test_files"
    test_dir.mkdir(exist_ok=True)
    yield test_dir
    # Clean up after all tests are done
    for item in test_dir.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            for subitem in item.iterdir():
                subitem.unlink()
            item.rmdir()

@pytest.fixture
def mock_dbt_client() -> MagicMock:
    """
    Mock the DbtClient for testing.
    
    Returns:
        MagicMock: Mocked DbtClient instance
    """
    with patch('snowplow_signals.dbt.cli.DbtClient') as mock:
        client = MagicMock()
        mock.return_value = client
        yield client

@pytest.fixture
def api_params() -> List[str]:
    """
    Common API parameters for testing.
    
    Returns:
        List[str]: List of API-related command line arguments
    """
    return [
        "--api-url", TEST_API_URL,
        "--api-key", TEST_API_KEY,
        "--api-key-id", TEST_API_KEY_ID,
        "--org-id", TEST_ORG_ID
    ]

def test_cli_init_project_succeeds(test_repo_dir: Path, mock_dbt_client: MagicMock, 
                            api_params: List[str]) -> None:
    """
    Test successful initialization of dbt project.
    
    Args:
        test_repo_dir: Path to test repository directory
        mock_dbt_client: Mocked DbtClient
        api_params: API-related command line arguments
    """
    mock_dbt_client.init_project.return_value = True
    
    with pytest.raises(SystemExit) as exc_info:
        app(['init', '--repo-path', str(test_repo_dir)] + api_params)
    
    assert exc_info.value.code == 0
    mock_dbt_client.init_project.assert_called_once_with(
        repo_path=str(test_repo_dir),
        view_name=None,
        view_version=None
    )

def test_cli_init_project_with_view_name_succeeds(test_repo_dir: Path, mock_dbt_client: MagicMock,
                                      api_params: List[str]) -> None:
    """
    Test initialization with specific view name.
    
    Args:
        test_repo_dir: Path to test repository directory
        mock_dbt_client: Mocked DbtClient
        api_params: API-related command line arguments
    """
    mock_dbt_client.init_project.return_value = True
    
    with pytest.raises(SystemExit) as exc_info:
        app(['init', '--repo-path', str(test_repo_dir), '--view-name', TEST_VIEW_NAME] + api_params)
    
    assert exc_info.value.code == 0
    mock_dbt_client.init_project.assert_called_once_with(
        repo_path=str(test_repo_dir),
        view_name=TEST_VIEW_NAME,
        view_version=None
    )

def test_cli_init_project_with_view_name_and_version_succeeds(test_repo_dir: Path, mock_dbt_client: MagicMock,
                                      api_params: List[str]) -> None:
    """
    Test initialization with specific view name and version.
    
    Args:
        test_repo_dir: Path to test repository directory
        mock_dbt_client: Mocked DbtClient
        api_params: API-related command line arguments
    """
    mock_dbt_client.init_project.return_value = True
    
    with pytest.raises(SystemExit) as exc_info:
        app(['init', '--repo-path', str(test_repo_dir), '--view-name', TEST_VIEW_NAME, '--view-version', str(TEST_VIEW_VERSION)] + api_params)
    
    assert exc_info.value.code == 0
    mock_dbt_client.init_project.assert_called_once_with(
        repo_path=str(test_repo_dir),
        view_name=TEST_VIEW_NAME,
        view_version=TEST_VIEW_VERSION
    )

def test_cli_init_project_fails(test_repo_dir: Path, mock_dbt_client: MagicMock,
                            api_params: List[str]) -> None:
    """
    Test initialization failure.
    
    Args:
        test_repo_dir: Path to test repository directory
        mock_dbt_client: Mocked DbtClient
        api_params: API-related command line arguments
    """
    mock_dbt_client.init_project.return_value = False
    
    with pytest.raises(SystemExit) as exc_info:
        app(['init', '--repo-path', str(test_repo_dir)] + api_params)
    
    assert exc_info.value.code == 1

def test_cli_generate_models_succeeds(test_repo_dir: Path, mock_dbt_client: MagicMock,
                                api_params: List[str]) -> None:
    """
    Test successful generation of dbt models.
    
    Args:
        test_repo_dir: Path to test repository directory
        mock_dbt_client: Mocked DbtClient
        api_params: API-related command line arguments
    """
    mock_dbt_client.generate_models.return_value = True
    
    with pytest.raises(SystemExit) as exc_info:
        app(['generate', '--repo-path', str(test_repo_dir)] + api_params)
    
    assert exc_info.value.code == 0
    mock_dbt_client.generate_models.assert_called_once_with(
        repo_path=str(test_repo_dir),
        project_name=None,
        update=False
    )

def test_cli_generate_models_with_update_succeeds(test_repo_dir: Path, mock_dbt_client: MagicMock,
                                    api_params: List[str]) -> None:
    """
    Test generation with update flag.
    
    Args:
        test_repo_dir: Path to test repository directory
        mock_dbt_client: Mocked DbtClient
        api_params: API-related command line arguments
    """
    mock_dbt_client.generate_models.return_value = True
    
    with pytest.raises(SystemExit) as exc_info:
        app(['generate', '--repo-path', str(test_repo_dir), '--update'] + api_params)
    
    assert exc_info.value.code == 0
    mock_dbt_client.generate_models.assert_called_once_with(
        repo_path=str(test_repo_dir),
        project_name=None,
        update=True
    )

def test_cli_generate_models_fails(test_repo_dir: Path, mock_dbt_client: MagicMock,
                                api_params: List[str]) -> None:
    """
    Test generation failure.
    
    Args:
        test_repo_dir: Path to test repository directory
        mock_dbt_client: Mocked DbtClient
        api_params: API-related command line arguments
    """
    mock_dbt_client.generate_models.return_value = False
    
    with pytest.raises(SystemExit) as exc_info:
        app(['generate', '--repo-path', str(test_repo_dir)] + api_params)
    
    assert exc_info.value.code == 1

def test_cli_commands_with_invalid_repo_path_fail(api_params: List[str]) -> None:
    """
    Test commands with invalid repository path.
    
    Args:
        api_params: API-related command line arguments
    """
    # Test init command with invalid path
    with pytest.raises(SystemExit) as exc_info:
        app(['init', '--repo-path', '/nonexistent/path'] + api_params)
    assert exc_info.value.code == 1
    
    # Test generate command with invalid path
    with pytest.raises(SystemExit) as exc_info:
        app(['generate', '--repo-path', '/nonexistent/path'] + api_params)
    assert exc_info.value.code == 1

def test_cli_commands_with_debug_logging_succeed(test_repo_dir: Path, mock_dbt_client: MagicMock,
                      api_params: List[str]) -> None:
    """
    Test commands with debug logging enabled.
    
    Args:
        test_repo_dir: Path to test repository directory
        mock_dbt_client: Mocked DbtClient
        api_params: API-related command line arguments
    """
    mock_dbt_client.init_project.return_value = True
    
    with pytest.raises(SystemExit) as exc_info:
        app(['init', '--repo-path', str(test_repo_dir), '--debug'] + api_params)
    
    assert exc_info.value.code == 0
    mock_dbt_client.init_project.assert_called_once()

def test_cli_commands_with_custom_api_url_succeed(test_repo_dir: Path, mock_dbt_client: MagicMock) -> None:
    """
    Test commands with custom API URL.
    
    Args:
        test_repo_dir: Path to test repository directory
        mock_dbt_client: Mocked DbtClient
    """
    mock_dbt_client.init_project.return_value = True
    custom_api_params = [
        "--api-url", "http://custom-api:8000",
        "--api-key", TEST_API_KEY,
        "--api-key-id", TEST_API_KEY_ID,
        "--org-id", TEST_ORG_ID
    ]
    
    with pytest.raises(SystemExit) as exc_info:
        app(['init', '--repo-path', str(test_repo_dir)] + custom_api_params)
    
    assert exc_info.value.code == 0
    mock_dbt_client.init_project.assert_called_once()

def test_cli_test_connection_succeeds(api_params: List[str], respx_mock) -> None:
    """
    Test successful API connection check.
    
    Args:
        api_params: API-related command line arguments
        respx_mock: HTTPX mock fixture
    """
    # Mock token request
    token_mock = respx_mock.get(
        f"https://console.snowplowanalytics.com/api/msc/v1/organizations/{TEST_ORG_ID}/credentials/v3/token"
    ).mock(return_value=httpx.Response(
        200,
        json={"accessToken": "test-token"}
    ))
    
    # Mock successful health check response
    health_mock = respx_mock.get(
        "http://localhost:8087/api/v1/health-all"
    ).mock(return_value=httpx.Response(
        200,
        json={
            "status": "ok",
            "dependencies": {
                "storage": "ok",
                "feature_server": "ok"
            }
        }
    ))
    
    with pytest.raises(SystemExit) as exc_info:
        app(['test-connection'] + api_params)
    
    assert exc_info.value.code == 0
    assert token_mock.called
    assert health_mock.called

def test_cli_test_connection_fails_with_down_status(api_params: List[str], respx_mock) -> None:
    """
    Test API connection check when service is down.
    
    Args:
        api_params: API-related command line arguments
        respx_mock: HTTPX mock fixture
    """
    # Mock token request
    token_mock = respx_mock.get(
        f"https://console.snowplowanalytics.com/api/msc/v1/organizations/{TEST_ORG_ID}/credentials/v3/token"
    ).mock(return_value=httpx.Response(
        200,
        json={"accessToken": "test-token"}
    ))
    
    # Mock failed health check response
    health_mock = respx_mock.get(
        "http://localhost:8087/api/v1/health-all"
    ).mock(return_value=httpx.Response(
        200,
        json={
            "status": "down",
            "dependencies": {
                "storage": "ok",
                "feature_server": "down"
            }
        }
    ))
    
    with pytest.raises(SystemExit) as exc_info:
        app(['test-connection'] + api_params)
    
    assert exc_info.value.code == 1
    assert token_mock.called
    assert health_mock.called

def test_cli_test_connection_fails_with_exception(api_params: List[str], respx_mock) -> None:
    """
    Test API connection check when an exception occurs.
    
    Args:
        api_params: API-related command line arguments
        respx_mock: HTTPX mock fixture
    """
    # Mock token request
    token_mock = respx_mock.get(
        f"https://console.snowplowanalytics.com/api/msc/v1/organizations/{TEST_ORG_ID}/credentials/v3/token"
    ).mock(return_value=httpx.Response(
        200,
        json={"accessToken": "test-token"}
    ))
    
    # Mock connection error
    health_mock = respx_mock.get(
        "http://localhost:8087/api/v1/health-all"
    ).mock(side_effect=httpx.ConnectError("Connection refused"))
    
    with pytest.raises(SystemExit) as exc_info:
        app(['test-connection'] + api_params)
    
    assert exc_info.value.code == 1
    assert token_mock.called
    assert health_mock.called

def test_cli_test_connection_with_debug_logging(api_params: List[str], respx_mock) -> None:
    """
    Test API connection check with debug logging enabled.
    
    Args:
        api_params: API-related command line arguments
        respx_mock: HTTPX mock fixture
    """
    # Mock token request
    token_mock = respx_mock.get(
        f"https://console.snowplowanalytics.com/api/msc/v1/organizations/{TEST_ORG_ID}/credentials/v3/token"
    ).mock(return_value=httpx.Response(
        200,
        json={"accessToken": "test-token"}
    ))
    
    # Mock successful health check response
    health_mock = respx_mock.get(
        "http://localhost:8087/api/v1/health-all"
    ).mock(return_value=httpx.Response(
        200,
        json={
            "status": "ok",
            "dependencies": {
                "storage": "ok",
                "feature_server": "ok"
            }
        }
    ))
    
    with pytest.raises(SystemExit) as exc_info:
        app(['test-connection', '--debug'] + api_params)
    
    assert exc_info.value.code == 0
    assert token_mock.called
    assert health_mock.called

def test_cli_test_connection_with_custom_api_url(api_params: List[str], respx_mock) -> None:
    """
    Test API connection check with custom API URL.
    
    Args:
        api_params: API-related command line arguments
        respx_mock: HTTPX mock fixture
    """
    custom_api_params = [
        "--api-url", "http://custom-api:8000",
        "--api-key", TEST_API_KEY,
        "--api-key-id", TEST_API_KEY_ID,
        "--org-id", TEST_ORG_ID
    ]
    
    # Mock token request
    token_mock = respx_mock.get(
        f"https://console.snowplowanalytics.com/api/msc/v1/organizations/{TEST_ORG_ID}/credentials/v3/token"
    ).mock(return_value=httpx.Response(
        200,
        json={"accessToken": "test-token"}
    ))
    
    # Mock successful health check response for custom URL
    health_mock = respx_mock.get(
        "http://custom-api:8000/api/v1/health-all"
    ).mock(return_value=httpx.Response(
        200,
        json={
            "status": "ok",
            "dependencies": {
                "storage": "ok",
                "feature_server": "ok"
            }
        }
    ))
    
    with pytest.raises(SystemExit) as exc_info:
        app(['test-connection'] + custom_api_params)
    
    assert exc_info.value.code == 0
    assert token_mock.called
    assert health_mock.called 