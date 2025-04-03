import json
import logging
import os

import typer
from typing_extensions import Annotated

from snowplow_signals.dbt.models.base_config_generator import (
    BaseConfigGenerator,
)
from snowplow_signals.logging import get_logger

from ...api_client import ApiClient
from ...models import ViewOutput
from ..utils.utils import filter_latest_model_version_by_name

logger = get_logger(__name__)


class DbtProjectSetup:
    """
    Base class for setting up the base dbt project(s) including the base config.
    """

    def __init__(
        self,
        api_client: ApiClient,
        repo_path: Annotated[str, typer.Option()] = "customer_repo",
        view_name: str | None = None,
        view_version: int | None = None,
    ):
        self.api_client = api_client
        self.repo_path = repo_path
        self.view_name = view_name
        self.view_version = view_version

    def create_project_directories(self, setup_project_name: str, base_config: dict):
        # Create project-specific output directory
        project_output_dir = os.path.join(self.repo_path, setup_project_name, "configs")
        if not os.path.exists(project_output_dir):
            os.makedirs(project_output_dir)
        base_config_path = os.path.join(project_output_dir, "base_config.json")
        with open(base_config_path, "w") as f:
            json.dump(base_config, f, indent=4)
        logger.success(f"📄 Base config file generated for {setup_project_name}")

    def get_attribute_view_project_config(
        self,
        attribute_view: ViewOutput,
        # FIXME return type to be based on create_base_config typed value
    ) -> dict:
        generator = BaseConfigGenerator(data=attribute_view)
        return generator.create_base_config()

    def setup_all_projects(self):
        """Sets up dbt files for one or all projects."""

        attribute_views = self._get_attribute_views()

        for attribute_view in attribute_views:
            view_project_name = f"{attribute_view.name}_{attribute_view.version}"
            project_config = self.get_attribute_view_project_config(attribute_view)
            self.create_project_directories(view_project_name, project_config)

        return True

    def _fetch_attribute_views(self) -> list[ViewOutput]:
        attribute_views = self.api_client.make_request(
            method="GET",
            endpoint="registry/views/",
            params={"offline": True},
        )
        return [ViewOutput.model_validate(view) for view in attribute_views]

    def _get_attribute_views(self) -> list[ViewOutput]:
        logger.info("🔗 Fetching attribute views from API")
        all_attribute_views = self._fetch_attribute_views()
        logger.debug(
            f"Received API response: {[view.model_dump_json() for view in all_attribute_views]}"
        )

        if len(all_attribute_views) == 0:
            raise ValueError("No attribute views available.")

        latest_views = filter_latest_model_version_by_name(all_attribute_views)

        # Filter by project name if specified
        if self.view_name:
            project_views = [
                view for view in latest_views if view.name == self.view_name
            ]
            if not project_views:
                raise ValueError(
                    f"No project/attribute view found with name: {self.view_name}"
                )
            return project_views
        else:
            return latest_views
