"""Command-line interface for dbt project generation functionality"""

import sys
from pathlib import Path
from typing import Optional
import os

import typer

from snowplow_signals.api_client import ApiClient
from snowplow_signals.batch_autogen import BatchAutogenClient
from snowplow_signals.logging import get_logger, setup_logging
from .cli_params import (
    API_KEY,
    API_KEY_ID,
    API_URL,
    CHECK_API,
    CHECK_AUTH,
    ORG_ID,
    PROJECT_NAME,
    REPO_PATH,
    UPDATE,
    VERBOSE,
    VIEW_NAME,
    VIEW_VERSION,
)

# Create the main Typer app with metadata
app = typer.Typer(
    help="Generate dbt projects for Snowplow signals data",
    add_completion=False,
    no_args_is_help=True,
)
# Configure logging
logger = get_logger(__name__)


def validate_repo_path(repo_path: str) -> Path:
    """Validate and convert repository path to Path object.
    Args:
        repo_path: Path to the repository
    Returns:
        Path: Validated repository path
    Raises:
        typer.BadParameter: If path is invalid
    """
    path = Path(repo_path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created repository directory: {repo_path}")
    if not path.is_dir():
        raise typer.BadParameter(f"Repository path is not a directory: {repo_path}")
    return path


def create_api_client(
    api_url: str,
    api_key: str,
    api_key_id: str,
    org_id: str,
) -> ApiClient:
    """Create an API client with the given credentials.
    Args:
        api_url: URL of the API server
        api_key: API key for authentication
        api_key_id: ID of the API key
        org_id: Organization ID
    Returns:
        ApiClient: Configured API client
    """
    return ApiClient(
        api_url=api_url,
        api_key=api_key,
        api_key_id=api_key_id,
        org_id=org_id,
    )


@app.command()
def init(
    api_url: API_URL,
    api_key: API_KEY,
    api_key_id: API_KEY_ID,
    org_id: ORG_ID,
    repo_path: REPO_PATH,
    view_name: VIEW_NAME = None,
    view_version: VIEW_VERSION = None,
    verbose: VERBOSE = False,
) -> None:
    """Initialize dbt project structure and base configuration."""
    try:
        setup_logging(verbose)
        validated_path = validate_repo_path(repo_path)
        logger.info(f"Initializing dbt project(s) in {validated_path}")
        api_client = create_api_client(api_url, api_key, api_key_id, org_id)
        client = BatchAutogenClient(api_client=api_client)
        success = client.init_project(
            repo_path=str(validated_path),
            view_name=view_name,
            view_version=view_version,
        )
        if not success:
            logger.error("Failed to initialize dbt project(s)")
            raise typer.Exit(code=1)
        logger.success("✅ Successfully initialized dbt project(s)")
    except Exception as e:
        logger.error(f"Error during project initialization: {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def generate(
    api_url: API_URL,
    api_key: API_KEY,
    api_key_id: API_KEY_ID,
    org_id: ORG_ID,
    repo_path: REPO_PATH,
    project_name: PROJECT_NAME = None,
    update: UPDATE = False,
    verbose: VERBOSE = False,
) -> None:
    """Generate dbt project assets such as data models, macros and config files."""
    try:
        setup_logging(verbose)
        validated_path = validate_repo_path(repo_path)
        logger.info(f"🛠️ Generating dbt models in {validated_path}")
        api_client = create_api_client(api_url, api_key, api_key_id, org_id)
        client = BatchAutogenClient(api_client=api_client)
        success = client.generate_models(
            repo_path=str(validated_path),
            project_name=project_name,
            update=update,
        )
        if not success:
            logger.error("Failed to generate dbt models")
            raise typer.Exit(code=1)
        logger.success("✅ Successfully generated dbt models")
    except Exception as e:
        logger.error(f"Error during model generation: {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def materialize(
    api_url: API_URL,
    api_key: API_KEY,
    api_key_id: API_KEY_ID,
    org_id: ORG_ID,
    view_name: VIEW_NAME,
    view_version: VIEW_VERSION,
    repo_path: REPO_PATH,
    verbose: VERBOSE = False,
) -> None:
    """Registers the attribute table as a data source so that the materialization process can start."""
    try:
        api_client = create_api_client(api_url, api_key, api_key_id, org_id)
        client = BatchAutogenClient(api_client=api_client)
        project_path = Path(repo_path) / f"{view_name}_{view_version}"
        client.materialize_model(
            project_path=project_path,
            view_name=view_name,
            view_version=view_version,
            verbose=verbose,
        )

    except Exception as e:
        logger.error(
            f"Error registering table {view_name}_{view_version}_attributes for materialization: {str(e)}"
        )
        raise typer.Exit(code=1)


@app.command()
def test_connection(
    api_url: API_URL,
    api_key: API_KEY,
    api_key_id: API_KEY_ID,
    org_id: ORG_ID,
    check_auth: CHECK_AUTH = True,
    check_api: CHECK_API = True,
    verbose: VERBOSE = False,
) -> None:
    """Test the connection to the authentication and API services."""
    try:
        setup_logging(verbose)
        api_client = create_api_client(api_url, api_key, api_key_id, org_id)
        auth_status = None
        api_status = None
        # Check authentication service if requested
        if check_auth:
            logger.info("🔐 Testing authentication service...")
            try:
                # Test auth by making a request to registry/views endpoint
                api_client.make_request(
                    method="GET", endpoint="registry/views/", params={"offline": True}
                )
                auth_status = {"status": "ok", "message": "Authentication successful"}
                logger.success("✅ Authentication service is healthy")
            except Exception as e:
                auth_status = {"status": "error", "message": str(e)}
                logger.error("❌ Authentication service is not responding")
                logger.error(f"   Error details: {str(e)}")
                logger.error(
                    "   Please check your API credentials and network connection"
                )
        # Check API service if requested
        if check_api:
            logger.info("🌐 Testing API service...")
            try:
                import httpx

                response = httpx.get(f"{api_url}/health-all")
                response.raise_for_status()
                health_response = response.json()
                if health_response["status"] == "ok":
                    api_status = {
                        "status": "ok",
                        "message": "API health check successful",
                        "dependencies": health_response["dependencies"],
                    }
                    logger.success("✅ API service is healthy")
                    logger.info("📊 Dependencies status:")
                    for dep, status in health_response["dependencies"].items():
                        status_symbol = "✅" if status == "ok" else "❌"
                        logger.info(f"   {status_symbol} {dep}: {status}")
                else:
                    api_status = {
                        "status": "error",
                        "message": "API health check failed",
                        "dependencies": health_response["dependencies"],
                    }
                    logger.error("❌ API service is not healthy")
                    logger.error("📊 Dependencies status:")
                    for dep, status in health_response["dependencies"].items():
                        status_symbol = "✅" if status == "ok" else "❌"
                        logger.error(f"   {status_symbol} {dep}: {status}")
            except Exception as e:
                error_msg = str(e)
                if not error_msg:
                    error_msg = "Unknown error occurred"
                if isinstance(e, httpx.HTTPStatusError):
                    try:
                        error_details = e.response.json()
                        logger.error(
                            f"❌ API service error (HTTP {e.response.status_code}): {error_details}"
                        )
                    except:
                        logger.error(
                            f"❌ API service error (HTTP {e.response.status_code}): {e.response.text}"
                        )
                else:
                    logger.error(f"❌ API service error: {error_msg}")
                logger.error("\n⚠️ API service is not operational")
                sys.exit(1)
        # Print summary of results
        logger.info("\n📋 Connection Test Results:")
        if check_auth and auth_status is not None:
            status_symbol = "✅" if auth_status["status"] == "ok" else "❌"
            logger.info(
                f"{status_symbol} Authentication Service: {auth_status['status']}"
            )
        if check_api and api_status is not None:
            status_symbol = "✅" if api_status["status"] == "ok" else "❌"
            logger.info(f"{status_symbol} API Service: {api_status['status']}")
        # Determine overall status
        if check_auth and check_api:
            if (
                auth_status is not None
                and api_status is not None
                and auth_status["status"] == "ok"
                and api_status["status"] == "ok"
            ):
                logger.success("\n✨ All services are operational!")
            else:
                logger.error("\n⚠️ Some services are not operational")
                sys.exit(1)
        elif (
            check_auth and auth_status is not None and auth_status["status"] == "error"
        ):
            logger.error("\n⚠️ Authentication service is not operational")
            sys.exit(1)
        elif check_api and api_status is not None and api_status["status"] == "error":
            logger.error("\n⚠️ API service is not operational")
            sys.exit(1)
        else:
            logger.success("\n✨ Selected services are operational!")
    except Exception as e:
        error_msg = str(e)
        if not error_msg:
            error_msg = "Unknown error occurred"
        logger.error(f"\n❌ Connection test failed: {error_msg}")
        sys.exit(1)


if __name__ == "__main__":
    app()
