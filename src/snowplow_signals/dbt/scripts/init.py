import argparse
import logging

from snowplow_dbt_autogen.models.dbt_project_setup import DbtProjectSetup

logger = logging.getLogger(__name__)


def configure_logging(debug: bool):
    """Set up logging level."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate base config for multiple dbt projects/attribute views."
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default="http://localhost:8087",
        help="Base URL of the API server",
    )
    parser.add_argument(
        "--no-api",
        action="store_true",
        help="Don't fetch from API, use local file instead",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--repo-path",
        type=str,
        required=True,
        help="Path containing multiple project/attribute view directories",
    )
    parser.add_argument(
        "--project-name",
        type=str,
        help="Optional name of a specific project/attribute view to process. If not provided, all projects will be processed.",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    configure_logging(args.debug)

    setup = DbtProjectSetup(
        api_url=args.api_url,
        use_api=not args.no_api,
        repo_path=args.repo_path,
        project_name=args.project_name,
    )

    setup.setup_all_projects()  # Keep method encapsulated in the class


if __name__ == "__main__":
    main()
