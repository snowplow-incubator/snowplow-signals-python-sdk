import json
import os
from typing import Optional
import json
from pathlib import Path

from snowplow_signals.batch_autogen.models.dbt_asset_generator import DbtAssetGenerator
from snowplow_signals.batch_autogen.models.dbt_config_generator import (
    DbtConfigGenerator,
)
from snowplow_signals.batch_autogen.models.batch_source_config import (
    BatchSourceConfig,
)
from snowplow_signals.batch_autogen.utils.utils import (
    batch_source_from_path,
)
from snowplow_signals.batch_autogen.models.dbt_project_setup import (
    DbtBaseConfig,
    DbtProjectSetup,
)
from snowplow_signals.logging import get_logger
from snowplow_signals.batch_autogen.models.dbt_project_setup import DbtProjectSetup
from snowplow_signals.logging import get_logger, setup_logging

from ..api_client import ApiClient

logger = get_logger(__name__)


class BatchAutogenClient:
    """Client for generating batch projects (dbt) for Snowplow data"""

    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def init_project(
        self,
        repo_path: str,
        view_name: str | None = None,
        view_version: int | None = None,
    ):
        """
        Initialize dbt project structure and base configuration.

        Args:
            repo_path: Path to the repository where projects will be stored
            view_name: Optional name of a specific attribute view project to initialize.
                         If None, all projects will be initialized.
            view_version: Optional version of the attribute view to initialize.
                         If None, the latest version will be used.
                         Only used if view_name is not None.
        """

        # TODO - Throw if version with no name -> Add overloads
        setup = DbtProjectSetup(
            api_client=self.api_client,
            repo_path=repo_path,
            view_name=view_name,
            view_version=view_version,
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
                    logger.error(
                        f"Failed to generate models for project: {project_name}"
                    )
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
                logger.error(
                    f"No project directories found with base_config.json in {repo_path}"
                )
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

    def _generate_project_assets(
        self, repo_path: str, project_name: str, update: bool = False
    ):
        """
        Generate dbt project assets for a specific project/attribute view.

        Args:
            repo_path: Base repository path containing multiple projects
            project_name: Project/attribute view directory name
            update: Whether to update existing files

        Returns:
            bool: Whether the generation was successful
        """
        project_path = Path(os.path.join(repo_path, project_name))
        base_config_path = Path(os.path.join(project_path, "configs/base_config.json"))
        dbt_config_path = Path(os.path.join(project_path, "configs/dbt_config.json"))

        if not os.path.exists(base_config_path):
            logger.warning(
                f"No base_config.json found for project {project_name}, skipping..."
            )
            return False

        logger.info(f"Processing project/attribute view: {project_name}")

        # Load base config and generate dbt config
        with open(base_config_path) as f:
            data = json.load(f)
            base_config = DbtBaseConfig.model_validate(data)

        generator = DbtConfigGenerator(base_config_data=base_config)
        dbt_config = generator.create_dbt_config()

        # Ensure configs directory exists
        os.makedirs(os.path.dirname(dbt_config_path), exist_ok=True)

        with open(dbt_config_path, "w") as f:
            json.dump(dbt_config.model_dump(), f, indent=4)

        logger.success(
            f"📄 Dbt Config file generated for {project_name}: dbt_config.json"
        )
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
                custom_context=dbt_config.filtered_events.model_dump(),
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
                custom_context=dbt_config.daily_agg.model_dump(),
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
                custom_context={"entity_key": base_config.entity_key},
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
            DbtAssetGenerator(
                project_path=project_path,
                asset_subpath="models/attributes",
                filename="attributes",
                asset_type="model",
                custom_context={**dbt_config.attributes.model_dump(), "entity_key": base_config.entity_key},
            ),
        ]

        try:
            for asset in assets:
                context = (
                    asset.custom_context
                    if asset.custom_context is not None
                    else dbt_config.model_dump()
                )
                asset.generate_asset(update=update, context=context)

            logger.success(f"✅ Finished generating models for {project_name}!")
            return True

        except ValueError as e:
            logger.error(f"❌ Error generating models for {project_name}: {e}")
            return False

    def materialize_model(
        self,
        project_path: str,
        view_name: str,
        view_version: int,
        verbose: bool = False,
    ):
        """
        Registers the batch source for the attributes table through the API and updates Feast so that materialization can begin.
        Args:
            project_path: Path to the repository where the dbt project is where the config file is stored.
            project_name: Name of a specific project (same as the unique view name and version).
            verbose: Optional flag to enable verbose logging
        """

        setup_logging(verbose)

        config_path = Path(project_path) / "configs" / "batch_source_config.json"
        table_name = f"{view_name}_{view_version}_attributes"

        batch_source_config = batch_source_from_path(
            config_path=str(config_path), table_name=table_name
        )

        self._register_batch_source(
            batch_source_config, view_name, view_version, table_name
        )
        self._update_registry(table_name)

    def _register_batch_source(
        self,
        batch_source_config: BatchSourceConfig,
        view_name: str,
        view_version: int,
        table_name: str,
    ):
        """Register batch source for table in the view"""

        logger.info(f"🛠️ Registering batch_source for table {table_name}.")

        try:
            view_update_endpoint = (
                f"registry/views/{view_name}/versions/{view_version}/batch_source"
            )
            data = batch_source_config.model_dump(mode="json", exclude_none=True)
            self.api_client.make_request(
                method="PUT", endpoint=view_update_endpoint, data=data
            )

            logger.success(
                f"✅ Successfully added Batch Source information to view {view_name}_{view_version}"
            )

        except Exception as e:
            logger.error(
                f"\n⚠️ The batch source couldn't be registered. Error: {str(e)}"
            )
            raise e

    def _update_registry(self, table_name: str):
        try:
            logger.info(f"🛠️ Updating registry")

            response = self.api_client.make_request(
                method="POST", endpoint="feature_store/apply"
            )
            if response.get("status") == "applied":
                logger.success(f"✅ Successfully registered table {table_name}")
        except Exception as e:
            logger.error(f"\n⚠️ The table {table_name} couldn't be registered.")
            raise e
