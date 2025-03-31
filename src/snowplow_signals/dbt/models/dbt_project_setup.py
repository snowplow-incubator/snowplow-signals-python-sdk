import json
import logging
import os

import typer
from typing_extensions import Annotated

from snowplow_signals.dbt.models.base_config_generator import (
    BaseConfigGenerator,
)

from ...api_client import ApiClient
from ...models import ViewOutput

logger = logging.getLogger(__name__)


class DbtProjectSetup:
    """
    Base class for setting up the base dbt project(s) including the base config.
    """

    def __init__(
        self,
        api_client: ApiClient,
        repo_path: Annotated[str, typer.Option()] = "customer_repo",
        project_name: str | None = None,
    ):
        self.api_client = api_client
        self.repo_path = repo_path
        self.project_name = project_name

    def setup_attribute_view_project(
        self, attribute_view: ViewOutput, setup_project_name: str
    ):
        """Creates the dbt project directory and required subdirectories."""
        print(
            "-------------------------------------------------------------------------------"
        )
        logger.info(f"Setting up dbt structure for project: {setup_project_name}")

        # Generate config for this project
        generator = BaseConfigGenerator(data=attribute_view)
        output = generator.create_base_config()

        # Create project-specific output directory
        project_output_dir = os.path.join(self.repo_path, setup_project_name, "configs")
        if not os.path.exists(project_output_dir):
            logger.info(f"Creating output directory: {project_output_dir}")
            os.makedirs(project_output_dir)

        # Save helper configs for this project (for debugging mainly)
        attribute_definitions_path = os.path.join(
            project_output_dir, "attribute_definitions.json"
        )
        with open(attribute_definitions_path, "w") as f:
            json.dump(attribute_view, f, indent=4)
        base_config_path = os.path.join(project_output_dir, "base_config.json")
        logger.info(
            f"✅ Attribute definitions saved for {setup_project_name}: {base_config_path}"
        )

        with open(base_config_path, "w") as f:
            json.dump(output, f, indent=4)
        logger.info(
            f"✅ Base config file generated for {setup_project_name}: {attribute_definitions_path}"
        )

    def setup_all_projects(self):
        """Sets up dbt files for one or all projects."""
        logger.info("Setting up dbt project(s)...")

        attribute_views = self._get_attribute_views()

        # FIXME What about versions ?
        for attribute_view in attribute_views:
            self.setup_attribute_view_project(attribute_view, attribute_view.name)

        logger.info("✅ Dbt project generation is finished!")
        return True

    def _fetch_attribute_views(self) -> list[ViewOutput]:
        attribute_views = self.api_client.make_request(
            method="GET",
            endpoint="registry/views/",
            params={"offline": True},
        )
        return [ViewOutput.model_validate(view) for view in attribute_views]

    def _get_attribute_views(self):
        logger.info("Fetching attribute views from API")
        all_attribute_views = self._fetch_attribute_views()
        logger.debug(
            f"Received API response: {json.dumps(all_attribute_views, indent=2)}"
        )

        if len(all_attribute_views) == 0:
            raise ValueError(f"No attribute views available.")

        # Filter by project name if specified
        if self.project_name:
            project_views = [
                view for view in all_attribute_views if view.name == self.project_name
            ]
            if not project_views:
                raise ValueError(
                    f"No project/attribute view found with name: {self.project_name}"
                )
            return project_views
        else:
            return all_attribute_views
