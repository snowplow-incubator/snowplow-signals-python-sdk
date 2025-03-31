"""Command-line interface for dbt project generation functionality"""

import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from snowplow_signals.dbt import DbtClient

# Create the main Typer app with metadata
app = typer.Typer(
    help="Generate dbt projects for Snowplow data",
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
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
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


@app.command()
def init(
    repo_path: Annotated[str, typer.Option(help="Path to the repository where projects will be stored")],
    project_name: Annotated[Optional[str], typer.Option(help="Optional name of a specific project to initialize")] = None,
    api_url: Annotated[Optional[str], typer.Option(help="URL of the API server to fetch schema information")] = None,
    debug: Annotated[bool, typer.Option(help="Enable debug logging")] = False,
) -> None:
    """Initialize dbt project structure and base configuration.
    
    This command sets up the basic dbt project structure including directories
    and configuration files. It can initialize either all projects or a specific
    project if project_name is provided.
    """
    try:
        setup_logging(debug)
        validated_path = validate_repo_path(repo_path)
        
        logger.info(f"Initializing dbt project(s) in {validated_path}")
        client = DbtClient(api_url=api_url)
        
        success = client.init_project(
            repo_path=str(validated_path),
            project_name=project_name
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
    repo_path: Annotated[str, typer.Option(help="Path to the repository where projects are stored")],
    project_name: Annotated[Optional[str], typer.Option(help="Optional name of a specific project to generate models for")] = None,
    update: Annotated[bool, typer.Option(help="Whether to update existing files")] = False,
    api_url: Annotated[Optional[str], typer.Option(help="URL of the API server to fetch schema information")] = None,
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
        client = DbtClient(api_url=api_url)
        
        success = client.generate_models(
            repo_path=str(validated_path),
            project_name=project_name,
            update=update
        )
        
        if not success:
            logger.error("Failed to generate dbt models")
            raise typer.Exit(code=1)
            
        logger.info("Successfully generated dbt models")
        
    except Exception as e:
        logger.error(f"Error during model generation: {str(e)}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app() 