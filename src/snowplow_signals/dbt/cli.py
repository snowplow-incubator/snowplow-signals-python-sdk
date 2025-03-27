"""Command-line interface for dbt project generation functionality"""

import logging
import typer
from typing import Optional
from typing_extensions import Annotated

from snowplow_signals.dbt import DbtClient

app = typer.Typer(help="Generate dbt projects for Snowplow data")
logger = logging.getLogger(__name__)


def setup_logging(debug: bool = False):
    """Configure logging level and format"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")


@app.command()
def init(
    repo_path: Annotated[str, typer.Option(help="Path to the repository where projects will be stored")],
    project_name: Annotated[Optional[str], typer.Option(help="Optional name of a specific project to initialize")] = None,
    api_url: Annotated[Optional[str], typer.Option(help="URL of the API server to fetch schema information")] = None,
    debug: Annotated[bool, typer.Option(help="Enable debug logging")] = False,
):
    """Initialize dbt project structure and base configuration"""
    setup_logging(debug)
    client = DbtClient(api_url=api_url)
    success = client.init_project(repo_path=repo_path, project_name=project_name)
    if not success:
        typer.echo("Failed to initialize dbt project(s)")
        raise typer.Exit(code=1)
    typer.echo("Successfully initialized dbt project(s)")


@app.command()
def generate(
    repo_path: Annotated[str, typer.Option(help="Path to the repository where projects are stored")],
    project_name: Annotated[Optional[str], typer.Option(help="Optional name of a specific project to generate models for")] = None,
    update: Annotated[bool, typer.Option(help="Whether to update existing files")] = False,
    debug: Annotated[bool, typer.Option(help="Enable debug logging")] = False,
):
    """Generate dbt project assets such as data models, macros and config files"""
    setup_logging(debug)
    client = DbtClient()
    success = client.generate_models(
        repo_path=repo_path, project_name=project_name, update=update
    )
    if not success:
        typer.echo("Failed to generate dbt models")
        raise typer.Exit(code=1)
    typer.echo("Successfully generated dbt models")


if __name__ == "__main__":
    app() 