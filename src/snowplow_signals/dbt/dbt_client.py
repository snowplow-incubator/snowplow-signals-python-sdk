"""Client for interacting with dbt project generation"""
import os
import logging
from typing import Optional

from snowplow_signals.dbt.models.dbt_project_setup import DbtProjectSetup
from snowplow_signals.dbt.models.dbt_asset_generator import DbtAssetGenerator
from snowplow_signals.dbt.models.dbt_config_generator import DbtConfigGenerator

logger = logging.getLogger(__name__)


class DbtClient:
    """Client for generating dbt projects for Snowplow data"""

    def __init__(self, api_url: Optional[str] = None):
        """
        Initialize the dbt client.

        Args:
            api_url: URL of the API server to fetch schema information.
        """
        self.api_url = api_url

    def init_project(self, repo_path: str, project_name: Optional[str] = None):
        """
        Initialize dbt project structure and base configuration.

        Args:
            repo_path: Path to the repository where projects will be stored
            project_name: Optional name of a specific project to initialize.
                         If None, all projects will be initialized.
        """
        setup = DbtProjectSetup(
            api_url=self.api_url,
            repo_path=repo_path,
            project_name=project_name,
        )

        return setup.setup_all_projects()

    def generate_models(
        self, repo_path: str, project_name: Optional[str] = None, update: bool = False
    ):
        """
        Generate dbt project assets such as data models, macros and config files.

        Args:
            repo_path: Path to the repository where projects are stored
            project_name: Optional name of a specific project to generate models for.
                         If None, models will be generated for all projects.
            update: Whether to update existing files
        """
        # If project name is specified, process only that project
        if project_name:
            if os.path.exists(os.path.join(repo_path, project_name)):
                success = self._generate_project_assets(repo_path, project_name, update)
                if not success:
                    logger.error(f"Failed to generate models for project: {project_name}")
                    return False
                return True
            else:
                logger.error(f"Project not found: {project_name}")
                return False
        else:
            # Process all project directories (any directory with a configs/base_config.json file)
            project_dirs = []
            for item in os.listdir(repo_path):
                if os.path.isdir(os.path.join(repo_path, item)) and os.path.exists(
                    os.path.join(repo_path, item, "configs", "base_config.json")
                ):
                    project_dirs.append(item)

            if not project_dirs:
                logger.error(f"No project directories found with base_config.json in {repo_path}")
                return False

            success_count = 0
            for project_dir in project_dirs:
                success = self._generate_project_assets(repo_path, project_dir, update)
                if success:
                    success_count += 1

            logger.info(
                f"✅ Processed {success_count} out of {len(project_dirs)} projects/attribute views"
            )
            return success_count > 0

    def _generate_project_assets(self, repo_path: str, project_name: str, update: bool = False):
        """
        Generate dbt project assets for a specific project/attribute view.

        Args:
            repo_path: Base repository path containing multiple projects
            project_name: Project/attribute view directory name
            update: Whether to update existing files

        Returns:
            bool: Whether the generation was successful
        """
        project_path = os.path.join(repo_path, project_name)
        base_config_path = os.path.join(project_path, "configs/base_config.json")
        dbt_config_path = os.path.join(project_path, "configs/dbt_config.json")

        if not os.path.exists(base_config_path):
            logger.warning(f"No base_config.json found for project {project_name}, skipping...")
            return False

        logger.info(f"Processing project/attribute view: {project_name}")

        # Load base config and generate dbt config
        with open(base_config_path) as f:
            import json
            data = json.load(f)

        generator = DbtConfigGenerator(base_config_data=data)
        output = generator.create_dbt_config()

        # Ensure configs directory exists
        os.makedirs(os.path.dirname(dbt_config_path), exist_ok=True)

        with open(dbt_config_path, "w") as f:
            json.dump(output, f, indent=4)

        logger.info(f"✅ Dbt Config file generated for {project_name}: dbt_config.json")
        logger.info(f"Generating dbt project assets for {project_name}...")

        # Define the assets to generate
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
                asset_subpath="",
                filename="packages",
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