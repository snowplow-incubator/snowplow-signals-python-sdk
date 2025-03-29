import json
import logging
import os
from typing import Optional

import typer
from pydantic import BaseModel
from typing_extensions import Annotated

from snowplow_signals.dbt.models.base_config_generator import (
    BaseConfigGenerator,
)
from snowplow_signals.dbt.scripts.fetch_attributes import fetch_attributes

logger = logging.getLogger(__name__)


class DbtProjectSetup(BaseModel):
    """
    Base class for setting up the base dbt project(s) including the base config.
    """

    api_url: Optional[str] = None
    use_api: bool = True
    repo_path: Annotated[str, typer.Option()] = "customer_repo"
    project_name: Optional[str] = None

    def setup_project(self, data, setup_project_name):
        """Creates the dbt project directory and required subdirectories."""
        print(
            "-------------------------------------------------------------------------------"
        )
        logger.info(f"Setting up dbt structure for project: {setup_project_name}")

        # Generate config for this project
        generator = BaseConfigGenerator(data=data)
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
            json.dump(data, f, indent=4)
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

        data = self._get_attribute_data()

        if self.project_name:
            self.setup_project(project_path, data, self.project_name)
        else:
            for attribute_data in data:
                current_project_name = attribute_data.get("name")
                if not current_project_name:
                    logger.warning("Found attribute data without name, skipping...")
                else:
                    self.setup_project(attribute_data, current_project_name)
                continue

        logger.info("✅ Dbt project generation is finished!")
        return True

    def _get_attribute_data(self):

        try:
            # Either fetch from API or load from local file
            if self.use_api:
                logger.info("Fetching attribute definitions from API")
                data = fetch_attributes(api_url=self.api_url, source_type="offline")

            else:
                logger.info("Loading attribute definitions from static config file")
                script_dir = os.path.dirname(os.path.abspath(__file__))
                static_config_path = os.path.join(
                    script_dir,
                    "..",
                    "..",
                    "..",
                    "integration_tests",
                    "local_testing",
                    "static_signals_config_offline.json",
                )

                with open(static_config_path) as f:
                    data = json.load(f)

            # Filter by project name if specified
            if self.project_name:
                data = [item for item in data if item.get("name") == self.project_name]
                if not data:
                    raise ValueError(
                        f"No project/attribute view found with name: {self.project_name}"
                    )

        except Exception as e:
            logger.error(f"Error generating config: {e}")
            raise
        return data
