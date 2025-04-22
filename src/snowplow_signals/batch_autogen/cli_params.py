from typing_extensions import Annotated
import typer
from typing import Optional

API_KEY = Annotated[
    str,
    typer.Option(
        help="API key for authentication",
        envvar="SNOWPLOW_API_KEY",
    ),
]

API_KEY_ID = Annotated[
    str,
    typer.Option(
        help="ID of the API key",
        envvar="SNOWPLOW_API_KEY_ID",
    ),
]

API_URL = Annotated[
    str,
    typer.Option(
        help="URL of the API server",
        envvar="SNOWPLOW_API_URL",
    ),
]

CHECK_API = Annotated[
    bool,
    typer.Option(
        help="Whether to check API service health",
        envvar="SNOWPLOW_CHECK_API",
    ),
]

CHECK_AUTH = Annotated[
    bool,
    typer.Option(
        help="Whether to check authentication service",
        envvar="SNOWPLOW_CHECK_AUTH",
    ),
]


ORG_ID = Annotated[
    str,
    typer.Option(
        help="Organization ID",
        envvar="SNOWPLOW_ORG_ID",
    ),
]

PROJECT_NAME = Annotated[
    Optional[str],
    typer.Option(
        help="Optional name of a specific project to generate models for",
        envvar="SNOWPLOW_PROJECT_NAME",
    ),
]


REPO_PATH = Annotated[
    str,
    typer.Option(
        help="Path to the repository for the dbt project(s)",
        envvar="SNOWPLOW_REPO_PATH",
    ),
]


UPDATE = Annotated[
    bool,
    typer.Option(
        help="Whether to update existing files",
        envvar="SNOWPLOW_UPDATE",
    ),
]


VERBOSE = Annotated[
    bool,
    typer.Option(
        "-v",
        "--verbose",
        help="Enable verbose output",
        envvar="SNOWPLOW_VERBOSE",
    ),
]


VIEW_NAME = Annotated[
    Optional[str],
    typer.Option(
        help="Name of a specific attribute view",
        envvar="SNOWPLOW_VIEW_NAME",
    ),
]

VIEW_VERSION = Annotated[
    Optional[int],
    typer.Option(
        help="Version of the attribute view",
        envvar="SNOWPLOW_VIEW_VERSION",
    ),
]
