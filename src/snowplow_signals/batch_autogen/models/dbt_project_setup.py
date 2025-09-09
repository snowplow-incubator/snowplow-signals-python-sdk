import json
import os
from typing import Literal

import typer
from typing_extensions import Annotated

from snowplow_signals.batch_autogen.models.base_config_generator import (
    BaseConfigGenerator,
    DbtBaseConfig,
)
from snowplow_signals.batch_autogen.models.batch_source_config import (
    BatchSourceConfig,
)
from snowplow_signals.cli_logging import get_logger

from ...api_client import ApiClient
from ...models import AttributeGroupResponse
from ..utils.utils import WarehouseType, filter_latest_model_version_by_name

logger = get_logger(__name__)


class DbtProjectSetup:
    """
    Base class for setting up the base dbt project(s) including the base config.
    """

    target_type: WarehouseType

    def __init__(
        self,
        api_client: ApiClient,
        target_type: WarehouseType,
        repo_path: Annotated[str, typer.Option()] = "customer_repo",
        attribute_group_name: str | None = None,
        attribute_group_version: int | None = None,
    ):
        self.api_client = api_client
        self.repo_path = repo_path
        self.attribute_group_name = attribute_group_name
        self.attribute_group_version = attribute_group_version
        self.target_type = target_type

    def create_project_directories(
        self,
        setup_project_name: str,
        base_config: DbtBaseConfig,
        batch_source_config: dict,
    ):
        # Create project-specific output directory
        project_output_dir = os.path.join(self.repo_path, setup_project_name, "configs")
        if not os.path.exists(project_output_dir):
            os.makedirs(project_output_dir)
        base_config_path = os.path.join(project_output_dir, "base_config.json")
        with open(base_config_path, "w") as f:
            json.dump(base_config.model_dump(), f, indent=4)
        logger.success(f"📄 Base config file generated for {setup_project_name}")
        batch_source_config_path = os.path.join(
            project_output_dir, "batch_source_config.json"
        )
        with open(batch_source_config_path, "w") as f:
            json.dump(batch_source_config, f, indent=4)
        logger.success(
            f"📄 Batch source config file generated for {setup_project_name}"
        )

    def _get_attribute_group_project_config(
        self,
        attribute_group: AttributeGroupResponse,
    ) -> DbtBaseConfig:
        generator = BaseConfigGenerator(
            data=attribute_group, target_type=self.target_type
        )
        return generator.create_base_config()

    def _get_default_batch_source_config(
        self, attribute_group: AttributeGroupResponse
    ) -> BatchSourceConfig:
        """
        Creates a pre-populated config file for users to fill out for the sync.
        """

        return BatchSourceConfig(
            database="",
            wh_schema="",
            table=f"{attribute_group.name}_{attribute_group.version}_attributes",
            name=f"{attribute_group.name}_{attribute_group.version}_attributes",
            timestamp_field="valid_at_tstamp",
            description=f"Table containing attributes for {attribute_group.name}_{attribute_group.version} attribute group",
            tags={},
            owner="",
        )

    def setup_all_projects(self):
        """Sets up dbt files for one or all projects."""

        attribute_groups = self._get_attribute_groups()
        for attribute_group in attribute_groups:
            # Skip attribute groups that have no attributes (i.e., only sync existing tables)
            if (not attribute_group.attributes) and attribute_group.fields:
                logger.info(
                    f"Skipping batch attribute group '{attribute_group.name}_{attribute_group.version}' as it has no attributes and only fields."
                )
                continue
            group_project_name = f"{attribute_group.name}_{attribute_group.version}"
            project_config = self._get_attribute_group_project_config(attribute_group)
            batch_source_config = self._get_default_batch_source_config(
                attribute_group
            ).model_dump(mode="json", exclude_none=True)
            self.create_project_directories(
                group_project_name, project_config, batch_source_config
            )

        return True

    def _fetch_attribute_groups(self) -> list[AttributeGroupResponse]:
        attribute_groups = self.api_client.make_request(
            method="GET",
            endpoint="registry/attribute_groups/",
            params={"offline": True, "property_syntax": self.target_type},
        )
        return [
            AttributeGroupResponse.model_validate(group) for group in attribute_groups
        ]

    def _get_attribute_groups(self) -> list[AttributeGroupResponse]:
        logger.info("🔗 Fetching attribute groups from API")
        all_attribute_groups = self._fetch_attribute_groups()
        logger.debug(
            f"Received API response: {[group.model_dump_json() for group in all_attribute_groups]}"
        )
        if len(all_attribute_groups) == 0:
            raise ValueError("No attribute groups available.")
        latest_groups = filter_latest_model_version_by_name(all_attribute_groups)
        # Filter by project name if specified
        if self.attribute_group_name:
            if not self.attribute_group_version:
                project_groups = [
                    group
                    for group in latest_groups
                    if group.name == self.attribute_group_name
                ]
                if not project_groups:
                    raise ValueError(
                        f"No project/attribute group found with name: {self.attribute_group_name}"
                    )
                return project_groups
            else:
                project_groups = [
                    group
                    for group in all_attribute_groups
                    if group.name == self.attribute_group_name
                    and group.version == self.attribute_group_version
                ]
                if not project_groups:
                    raise ValueError(
                        f"No project/attribute group found with name: {self.attribute_group_name} and version: {self.attribute_group_version}"
                    )
                return project_groups
        else:
            return latest_groups
