"""Command-line interface for dbt project generation functionality"""

import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from snowplow_signals.api_client import ApiClient
from snowplow_signals.dbt import DbtClient

# Create the main Typer app with metadata
app = typer.Typer(
    help="Generate dbt projects for Snowplow signals data",
    add_completion=False,
    no_args_is_help=True,
)

# Configure logging
logger = logging.getLogger(__name__)


def setup_logging(debug: bool = False) -> None:
    """Configure logging level and format with consistent styling.

    Args:
        debug: Whether to enable debug logging
    """
    level = logging.DEBUG if debug else logging.INFO
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)


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
        raise typer.BadParameter(f"Repository path does not exist: {repo_path}")
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
    api_url: Annotated[
        str, typer.Option(help="URL of the API server to fetch schema information")
    ],
    api_key: Annotated[str, typer.Option(help="API key for authentication")],
    api_key_id: Annotated[str, typer.Option(help="ID of the API key")],
    org_id: Annotated[str, typer.Option(help="Organization ID")],
    repo_path: Annotated[
        str, typer.Option(help="Path to the repository where projects will be stored")
    ],
    view_name: Annotated[
        Optional[str],
        typer.Option(
            help="Optional name of a specific attribute view project to initialize"
        ),
    ] = None,
    view_version: Annotated[
        Optional[int],
        typer.Option(
            help="Optional version of the attribute view to initialize. Only used if view_name is provided"
        ),
    ] = None,
    debug: Annotated[bool, typer.Option(help="Enable debug logging")] = False,
) -> None:
    """Initialize dbt project structure and base configuration.

    This command sets up the basic dbt project structure including directories
    and configuration files. It can initialize either all projects or a specific
    attribute view project if view_name is provided.
    """
    try:
        setup_logging(debug)
        validated_path = validate_repo_path(repo_path)

        logger.info(f"Initializing dbt project(s) in {validated_path}")
        api_client = create_api_client(api_url, api_key, api_key_id, org_id)
        client = DbtClient(api_client=api_client)

        success = client.init_project(
            repo_path=str(validated_path),
            view_name=view_name,
            view_version=view_version,
        )

        if not success:
            logger.error("Failed to initialize dbt project(s)")
            raise typer.Exit(code=1)

        logger.info("Successfully initialized dbt project(s)")

    except Exception as e:
        logger.error(f"Error during project initialization: {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def generate(
    api_url: Annotated[
        str, typer.Option(help="URL of the API server to fetch schema information")
    ],
    api_key: Annotated[str, typer.Option(help="API key for authentication")],
    api_key_id: Annotated[str, typer.Option(help="ID of the API key")],
    org_id: Annotated[str, typer.Option(help="Organization ID")],
    repo_path: Annotated[
        str, typer.Option(help="Path to the repository where projects are stored")
    ],
    project_name: Annotated[
        Optional[str],
        typer.Option(help="Optional name of a specific project to generate models for"),
    ] = None,
    update: Annotated[
        bool, typer.Option(help="Whether to update existing files")
    ] = False,
    debug: Annotated[bool, typer.Option(help="Enable debug logging")] = False,
) -> None:
    """Generate dbt project assets such as data models, macros and config files.

    This command generates all necessary dbt assets including models, macros,
    and configuration files. It can generate assets for either all projects
    or a specific project if project_name is provided.
    """
    try:
        setup_logging(debug)
        validated_path = validate_repo_path(repo_path)

        logger.info(f"Generating dbt models in {validated_path}")
        api_client = create_api_client(api_url, api_key, api_key_id, org_id)
        client = DbtClient(api_client=api_client)

        success = client.generate_models(
            repo_path=str(validated_path), project_name=project_name, update=update
        )

        if not success:
            logger.error("Failed to generate dbt models")
            raise typer.Exit(code=1)

        logger.info("Successfully generated dbt models")

    except Exception as e:
        logger.error(f"Error during model generation: {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def test_connection(
    api_url: Annotated[
        str, typer.Option(help="URL of the API server to test connection")
    ],
    api_key: Annotated[str, typer.Option(help="API key for authentication")],
    api_key_id: Annotated[str, typer.Option(help="ID of the API key")],
    org_id: Annotated[str, typer.Option(help="Organization ID")],
    check_auth: Annotated[
        bool, typer.Option(help="Whether to check authentication service")
    ] = True,
    check_api: Annotated[
        bool, typer.Option(help="Whether to check API service health")
    ] = True,
    debug: Annotated[bool, typer.Option(help="Enable debug logging")] = False,
) -> None:
    """Test the connection to the authentication and API services.

    This command can test both the authentication service and the API service health.
    You can choose to test either or both services using the --check-auth and --check-api flags.

    Authentication check verifies your credentials are valid.
    API health check verifies the API service and its dependencies are operational.
    """
    try:
        setup_logging(debug)
        api_client = create_api_client(api_url, api_key, api_key_id, org_id)

        auth_status = None
        api_status = None

        # Check authentication service if requested
        if check_auth:
            logger.info("Testing authentication service...")
            try:
                # Test auth by making a request to registry/views endpoint
                api_client.make_request(
                    method="GET", endpoint="registry/views/", params={"offline": True}
                )
                auth_status = {"status": "ok", "message": "Authentication successful"}
                logger.info("✅ Authentication successful!")
            except Exception as e:
                auth_status = {"status": "error", "message": str(e)}
                logger.error("❌ Authentication failed!")
                logger.error(f"Error: {str(e)}")

        # Check API service if requested
        if check_api:
            logger.info("Testing API service health...")
            try:
                health_response = api_client.make_request(
                    method="GET", endpoint="health-all"
                )

                if health_response["status"] == "ok":
                    api_status = {
                        "status": "ok",
                        "message": "API health check successful",
                        "dependencies": health_response["dependencies"],
                    }
                    logger.info("✅ API health check successful!")
                    logger.info("Dependencies status:")
                    for dep, status in health_response["dependencies"].items():
                        status_symbol = "✅" if status == "ok" else "❌"
                        logger.info(f"  {status_symbol} {dep}: {status}")
                else:
                    api_status = {
                        "status": "error",
                        "message": "API health check failed",
                        "dependencies": health_response["dependencies"],
                    }
                    logger.error("❌ API health check failed!")
                    logger.error("Dependencies status:")
                    for dep, status in health_response["dependencies"].items():
                        status_symbol = "✅" if status == "ok" else "❌"
                        logger.error(f"  {status_symbol} {dep}: {status}")
            except Exception as e:
                api_status = {"status": "error", "message": str(e)}
                logger.error(f"❌ Error checking API health: {str(e)}")

        # Determine overall status
        if check_auth and check_api:
            if (
                auth_status
                and api_status
                and auth_status["status"] == "ok"
                and api_status["status"] == "ok"
            ):
                logger.info("✅ All services operational!")
            else:
                logger.error("❌ Some services are not operational")
                raise typer.Exit(code=1)
        elif check_auth and auth_status and auth_status["status"] == "error":
            logger.error("❌ Authentication service is not operational")
            raise typer.Exit(code=1)
        elif check_api and api_status and api_status["status"] == "error":
            logger.error("❌ API service is not operational")
            raise typer.Exit(code=1)
        else:
            logger.info("✅ Selected services operational!")

    except Exception as e:
        logger.error(f"❌ Error during connection test: {str(e)}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
