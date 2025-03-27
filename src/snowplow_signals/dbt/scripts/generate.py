import argparse
import glob
import json
import logging
import os

import typer
from typing_extensions import Annotated

from snowplow_signals.dbt.models.dbt_asset_generator import DbtAssetGenerator
from snowplow_signals.dbt.models.dbt_config_generator import DbtConfigGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def generate_project_assets(repo_path: str, project_name: str, update: bool = False):
    """
    Generate dbt project assets such as data models, macros and config files for a specific project/attribute view

    Args:
        repo_path (str): Base repository path containing multiple projects
        project_name (str): Project/attribute view directory name
        update (bool): Whether to update existing files
    """
    project_path = os.path.join(repo_path, project_name)
    base_config_path = os.path.join(project_path, "utils/base_config.json")
    dbt_config_path = os.path.join(project_path, "utils/dbt_config.json")

    if not os.path.exists(base_config_path):
        logger.warning(f"No base_config.json found for project {project_name}, skipping...")
        return False

    print("-------------------------------------------------------------------------------")
    logger.info(f"Processing project/attribute view: {project_name}")

    with open(base_config_path) as f:
        data = json.load(f)

    generator = DbtConfigGenerator(base_config_data=data)
    output = generator.create_dbt_config()

    # Ensure utils directory exists
    os.makedirs(os.path.dirname(dbt_config_path), exist_ok=True)

    with open(dbt_config_path, "w") as f:
        json.dump(output, f, indent=4)

    logger.info(f"✅ Dbt Config file generated for {project_name}: dbt_config.json")

    logger.info(f"Generating dbt project assets for {project_name}...")

    assets = [
        DbtAssetGenerator(
            project_path=project_path,
            asset_subpath="models/base/scratch",
            filename="base_events_this_run",
            asset_type="model",
        ),
        DbtAssetGenerator(
            project_path=project_path,
            asset_subpath="models/base/scratch",
            filename="base_new_event_limits",
            asset_type="model",
        ),
        DbtAssetGenerator(
            project_path=project_path,
            asset_subpath="models/filtered_events/scratch",
            filename="filtered_events_this_run",
            asset_type="model",
            custom_context=output["filtered_events"],
        ),
        DbtAssetGenerator(
            project_path=project_path,
            asset_subpath="models/filtered_events",
            filename="filtered_events",
            asset_type="model",
        ),
        DbtAssetGenerator(
            project_path=project_path,
            asset_subpath="models/daily_aggregates/scratch",
            filename="daily_aggregates_this_run",
            asset_type="model",
            custom_context=output["daily_agg"],
        ),
        DbtAssetGenerator(
            project_path=project_path,
            asset_subpath="models/daily_aggregates/manifest",
            filename="daily_aggregation_manifest",
            asset_type="model",
        ),
        DbtAssetGenerator(
            project_path=project_path,
            asset_subpath="models/daily_aggregates/scratch",
            filename="days_to_process",
            asset_type="model",
        ),
        DbtAssetGenerator(
            project_path=project_path,
            asset_subpath="models/daily_aggregates",
            filename="daily_aggregates",
            asset_type="model",
        ),
        DbtAssetGenerator(
            project_path=project_path,
            asset_subpath="models/attributes",
            filename="attributes",
            asset_type="model",
            custom_context=output["attributes"],
        ),
        DbtAssetGenerator(
            project_path=project_path,
            asset_subpath="macros",
            filename="get_limits_for_attributes",
            asset_type="macro",
        ),
        DbtAssetGenerator(
            project_path=project_path,
            asset_subpath="macros",
            filename="allow_refresh",
            asset_type="macro",
        ),
        DbtAssetGenerator(
            project_path=project_path,
            asset_subpath="macros",
            filename="get_cluster_by_values",
            asset_type="macro",
        ),
        DbtAssetGenerator(
            project_path=project_path,
            asset_subpath="",
            filename="dbt_project",
            asset_type="yml",
        ),
        DbtAssetGenerator(
            project_path=project_path,
            asset_subpath="models/base/manifest",
            filename="incremental_manifest",
            asset_type="model",
        ),
    ]

    try:
        for asset in assets:
            context = (
                asset.custom_context
                if getattr(asset, "custom_context", None) is not None
                else output
            )
            asset.generate_asset(update=update, context=context)

        logger.info(f"✅ Finished generating models for {project_name}!")
        return True

    except ValueError as e:
        logger.error(f"Error generating models for {project_name}: {e}")
        return False


def generate(
    update: Annotated[bool, typer.Option()] = False,
    repo_path: Annotated[str, typer.Option()] = "customer_repo",
    project_name: Annotated[str, typer.Option()] = None,
):
    """
    Generate dbt project assets such as data models, macros and config files for all projects/attribute views or a specific one

    Args:
        update (bool): Whether to update existing files
        repo_path (str): Directory containing multiple project/attribute view directories
        project_name (str): Optional name of specific project to process. If None, process all projects.
    """
    if not os.path.exists(repo_path):
        logger.error(f"Customer repository path not found: {repo_path}")
        raise typer.Exit(code=1)

    # If project name is specified, process only that project
    if project_name:
        if os.path.exists(os.path.join(repo_path, project_name)):
            success = generate_project_assets(repo_path, project_name, update)
            if not success:
                logger.error(f"Failed to generate models for project: {project_name}")
                raise typer.Exit(code=1)
        else:
            logger.error(f"Project not found: {project_name}")
            raise typer.Exit(code=1)
    else:
        # Process all project directories (any directory with a utils/base_config.json file)
        project_dirs = []
        for item in os.listdir(repo_path):
            if os.path.isdir(os.path.join(repo_path, item)) and os.path.exists(
                os.path.join(repo_path, item, "utils", "base_config.json")
            ):
                project_dirs.append(item)

        if not project_dirs:
            logger.error(f"No project directories found with base_config.json in {repo_path}")
            raise typer.Exit(code=1)

        success_count = 0
        for project_dir in project_dirs:
            success = generate_project_assets(repo_path, project_dir, update)
            if success:
                success_count += 1

        logger.info(
            f"✅ Processed {success_count} out of {len(project_dirs)} projects/attribute views"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate DBT models for multiple projects/attribute views"
    )
    parser.add_argument(
        "--repo-path",
        type=str,
        required=True,
        help="Path containing multiple project/attribute view directories",
    )
    parser.add_argument("--update", action="store_true", help="Update existing files")
    parser.add_argument(
        "--project-name",
        type=str,
        help="Optional name of specific project/attribute view to process",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    generate(
        update=args.update,
        repo_path=args.repo_path,
        project_name=args.project_name,
    )
