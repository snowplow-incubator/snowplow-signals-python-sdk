"""
Tests for the CLI interface of the dbt model generation tool.
Verifies command-line argument handling and command execution.
"""

from pathlib import Path
from typing import Generator, List
from unittest.mock import MagicMock, patch

import pytest
import typer

from snowplow_signals.dbt.cli import app
from test.utils import (
    MOCK_API_KEY,
    MOCK_API_KEY_ID,
    MOCK_API_URL,
    MOCK_ORG_ID,
    MOCK_VIEW_NAME,
    MOCK_VIEW_VERSION,
)


@pytest.fixture(scope="session")
def test_repo_dir() -> Generator[Path, None, None]:
    """
    Create a persistent directory for testing.

    Returns:
        Generator[Path, None, None]: Path to the test directory

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
def mock_dbt_client() -> Generator[MagicMock, None, None]:
    """
    Mock the DbtClient for testing.

    Returns:
        Generator[MagicMock, None, None]: Mocked DbtClient instance
    """
    with patch("snowplow_signals.dbt.cli.DbtClient") as mock:
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
        "--api-url",
        MOCK_API_URL,
        "--api-key",
        MOCK_API_KEY,
        "--api-key-id",
        MOCK_API_KEY_ID,
        "--org-id",
        MOCK_ORG_ID,
    ]


def test_cli_init_project_succeeds(
    test_repo_dir: Path, mock_dbt_client: MagicMock, api_params: List[str]
) -> None:
    """
    Test successful initialization of dbt project.

    Args:
        test_repo_dir: Path to test repository directory
        mock_dbt_client: Mocked DbtClient
        api_params: API-related command line arguments
    """
    mock_dbt_client.init_project.return_value = True

    with pytest.raises(SystemExit) as exc_info:
        app(["init", "--repo-path", str(test_repo_dir)] + api_params)

    assert exc_info.value.code == 0
    mock_dbt_client.init_project.assert_called_once_with(
        repo_path=str(test_repo_dir), view_name=None, view_version=None
    )


def test_cli_init_project_with_view_name_succeeds(
    test_repo_dir: Path, mock_dbt_client: MagicMock, api_params: List[str]
) -> None:
    """
    Test initialization with specific view name.

    Args:
        test_repo_dir: Path to test repository directory
        mock_dbt_client: Mocked DbtClient
        api_params: API-related command line arguments
    """
    mock_dbt_client.init_project.return_value = True

    with pytest.raises(SystemExit) as exc_info:
        app(
            ["init", "--repo-path", str(test_repo_dir), "--view-name", MOCK_VIEW_NAME]
            + api_params
        )

    assert exc_info.value.code == 0
    mock_dbt_client.init_project.assert_called_once_with(
        repo_path=str(test_repo_dir), view_name=MOCK_VIEW_NAME, view_version=None
    )


def test_cli_init_project_with_view_name_and_version_succeeds(
    test_repo_dir: Path, mock_dbt_client: MagicMock, api_params: List[str]
) -> None:
    """
    Test initialization with specific view name and version.

    Args:
        test_repo_dir: Path to test repository directory
        mock_dbt_client: Mocked DbtClient
        api_params: API-related command line arguments
    """
    mock_dbt_client.init_project.return_value = True

    with pytest.raises(SystemExit) as exc_info:
        app(
            [
                "init",
                "--repo-path",
                str(test_repo_dir),
                "--view-name",
                MOCK_VIEW_NAME,
                "--view-version",
                str(MOCK_VIEW_VERSION),
            ]
            + api_params
        )

    assert exc_info.value.code == 0
    mock_dbt_client.init_project.assert_called_once_with(
        repo_path=str(test_repo_dir),
        view_name=MOCK_VIEW_NAME,
        view_version=MOCK_VIEW_VERSION,
    )


def test_cli_init_project_fails(
    test_repo_dir: Path, mock_dbt_client: MagicMock, api_params: List[str]
) -> None:
    """
    Test initialization failure.

    Args:
        test_repo_dir: Path to test repository directory
        mock_dbt_client: Mocked DbtClient
        api_params: API-related command line arguments
    """
    mock_dbt_client.init_project.return_value = False

    with pytest.raises(SystemExit) as exc_info:
        app(["init", "--repo-path", str(test_repo_dir)] + api_params)

    assert exc_info.value.code == 1


def test_cli_generate_models_succeeds(
    test_repo_dir: Path, mock_dbt_client: MagicMock, api_params: List[str]
) -> None:
    """
    Test successful generation of dbt models.

    Args:
        test_repo_dir: Path to test repository directory
        mock_dbt_client: Mocked DbtClient
        api_params: API-related command line arguments
    """
    mock_dbt_client.generate_models.return_value = True

    with pytest.raises(SystemExit) as exc_info:
        app(["generate", "--repo-path", str(test_repo_dir)] + api_params)

    assert exc_info.value.code == 0
    mock_dbt_client.generate_models.assert_called_once_with(
        repo_path=str(test_repo_dir), project_name=None, update=False
    )


def test_cli_generate_models_with_update_succeeds(
    test_repo_dir: Path, mock_dbt_client: MagicMock, api_params: List[str]
) -> None:
    """
    Test generation with update flag.

    Args:
        test_repo_dir: Path to test repository directory
        mock_dbt_client: Mocked DbtClient
        api_params: API-related command line arguments
    """
    mock_dbt_client.generate_models.return_value = True

    with pytest.raises(SystemExit) as exc_info:
        app(["generate", "--repo-path", str(test_repo_dir), "--update"] + api_params)

    assert exc_info.value.code == 0
    mock_dbt_client.generate_models.assert_called_once_with(
        repo_path=str(test_repo_dir), project_name=None, update=True
    )


def test_cli_generate_models_fails(
    test_repo_dir: Path, mock_dbt_client: MagicMock, api_params: List[str]
) -> None:
    """
    Test generation failure.

    Args:
        test_repo_dir: Path to test repository directory
        mock_dbt_client: Mocked DbtClient
        api_params: API-related command line arguments
    """
    mock_dbt_client.generate_models.return_value = False

    with pytest.raises(SystemExit) as exc_info:
        app(["generate", "--repo-path", str(test_repo_dir)] + api_params)

    assert exc_info.value.code == 1


def test_cli_commands_with_invalid_repo_path_fail(api_params: List[str]) -> None:
    """
    Test commands with invalid repository path.

    Args:
        api_params: API-related command line arguments
    """
    # Test init command with invalid path
    with pytest.raises(SystemExit) as exc_info:
        app(["init", "--repo-path", "/nonexistent/path"] + api_params)
    assert exc_info.value.code == 1

    # Test generate command with invalid path
    with pytest.raises(SystemExit) as exc_info:
        app(["generate", "--repo-path", "/nonexistent/path"] + api_params)
    assert exc_info.value.code == 1


def test_cli_commands_with_debug_logging_succeed(
    test_repo_dir: Path, mock_dbt_client: MagicMock, api_params: List[str]
) -> None:
    """
    Test commands with debug logging enabled.

    Args:
        test_repo_dir: Path to test repository directory
        mock_dbt_client: Mocked DbtClient
        api_params: API-related command line arguments
    """
    mock_dbt_client.init_project.return_value = True

    with pytest.raises(SystemExit) as exc_info:
        app(["init", "--repo-path", str(test_repo_dir), "--debug"] + api_params)

    assert exc_info.value.code == 0
    mock_dbt_client.init_project.assert_called_once()


def test_cli_commands_with_custom_api_url_succeed(
    test_repo_dir: Path, mock_dbt_client: MagicMock
) -> None:
    """
    Test commands with custom API URL.

    Args:
        test_repo_dir: Path to test repository directory
        mock_dbt_client: Mocked DbtClient
    """
    mock_dbt_client.init_project.return_value = True
    custom_api_params = [
        "--api-url",
        "http://custom-api:8000",
        "--api-key",
        MOCK_API_KEY,
        "--api-key-id",
        MOCK_API_KEY_ID,
        "--org-id",
        MOCK_ORG_ID,
    ]

    with pytest.raises(SystemExit) as exc_info:
        app(["init", "--repo-path", str(test_repo_dir)] + custom_api_params)

    assert exc_info.value.code == 0
    mock_dbt_client.init_project.assert_called_once()


def test_validate_repo_path_creates_directory(test_repo_dir: Path) -> None:
    """Test validate_repo_path creates directory when it doesn't exist."""
    from snowplow_signals.dbt.cli import validate_repo_path

    # Create a non-existent path
    non_existent_path = test_repo_dir / "new_directory"

    # Ensure the path doesn't exist
    if non_existent_path.exists():
        non_existent_path.rmdir()

    # Validate the path - should create the directory
    result = validate_repo_path(str(non_existent_path))

    # Verify the directory was created
    assert result.exists()
    assert result.is_dir()

    # Clean up
    non_existent_path.rmdir()


def test_validate_repo_path_fails_with_file(test_repo_dir: Path) -> None:
    """Test validate_repo_path when path exists but is not a directory."""
    from snowplow_signals.dbt.cli import validate_repo_path

    # Create a file instead of a directory
    test_file = test_repo_dir / "test_file.txt"
    test_file.touch()

    with pytest.raises(typer.BadParameter) as exc_info:
        validate_repo_path(str(test_file))

    assert "is not a directory" in str(exc_info.value)

    # Clean up
    test_file.unlink()
