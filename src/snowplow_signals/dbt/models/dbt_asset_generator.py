import logging
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel

from snowplow_signals.dbt.utils.utils import write_file
from snowplow_signals.logging import get_logger

logger = get_logger(__name__)


class DbtAssetGenerator(BaseModel):
    """
    Base class for auto-generating dbt components like models, macros, and configs.
    """

    project_path: Path
    asset_subpath: str
    filename: str
    asset_type: str
    custom_context: Optional[dict] = None

    @property
    def project_name(self) -> str:
        """Extracts the project name from the project path."""
        return Path(self.project_path).name

    def _jinja_environment(self) -> Environment:
        loader = FileSystemLoader([Path(__file__).parent.parent / "templates"])
        env = Environment(loader=loader, autoescape=select_autoescape())
        env.globals["project_name"] = self.project_name
        env.globals["model"] = self
        return env

    def get_filepath(self) -> Path:
        """Public method to return the constructed filepath."""
        return self._build_filepath()

    def _build_filepath(self) -> Path:
        """Private helper to construct the dbt asset file path."""
        if (self._get_file_type() == "yml") or (self.asset_type == "macro"):
            return Path(
                self.project_path
                / self.asset_subpath
                / f"{self.filename}.{self._get_file_type()}"
            )
        else:
            return Path(
                self.project_path
                / self.asset_subpath
                / f"{self.project_name}_{self.filename}.{self._get_file_type()}"
            )

    def _get_file_type(self) -> str:

        if self.asset_type == "model":
            return "sql"
        elif self.asset_type == "macro":
            return "sql"
        elif self.asset_type == "yml":
            return "yml"
        else:
            raise ValueError(f"Invalid asset type: {self.asset_type}")

    def generate_asset(self, update: bool, context: dict) -> None:
        env = self._jinja_environment()
        template = env.get_template(self.filename + ".j2")
        write_file(self.get_filepath(), template.render(**context))
        ## file emoji
        logger.info(f"📄 {self.asset_type.capitalize()}: {self.filename} generated")
