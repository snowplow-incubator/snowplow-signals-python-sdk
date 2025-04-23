from pathlib import Path
from typing import Any, Literal

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from pydantic import BaseModel, ConfigDict, Field

from snowplow_signals.batch_autogen.utils.utils import write_file
from snowplow_signals.logging import get_logger

logger = get_logger(__name__)

AssetTypeLiteral = Literal["model", "macro", "yml"]
FileTypeLiteral = Literal["sql", "yml"]


class DbtAssetGenerator(BaseModel):
    """
    Base class for auto-generating dbt components like models, macros, and configs.

    Attributes:
        project_path: Path to the dbt project root
        asset_subpath: Subpath within the project for the asset
        filename: Name of the file to generate (without extension)
        asset_type: Type of dbt asset (model, macro, or yml)
        custom_context: Optional custom context for template rendering
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,  # Allow Path type
        validate_assignment=True,  # Validate when attributes are set
    )

    project_path: Path = Field(description="Path to the dbt project root")
    asset_subpath: str = Field(description="Subpath within the project for the asset")
    filename: str = Field(
        description="Name of the file to generate (without extension)"
    )
    asset_type: AssetTypeLiteral = Field(
        description="Type of dbt asset (model, macro, or yml)"
    )
    custom_context: dict[str, Any] | None = Field(
        default=None, description="Optional custom context for template rendering"
    )

    @property
    def project_name(self) -> str:
        """Extracts the project name from the project path."""
        return self.project_path.name

    def _jinja_environment(self) -> Environment:
        """Creates and configures a Jinja environment for template rendering."""
        template_path = Path(__file__).parent.parent / "templates"
        if not template_path.exists():
            raise FileNotFoundError(f"Template directory not found: {template_path}")

        loader = FileSystemLoader([template_path])
        env = Environment(loader=loader, autoescape=select_autoescape())
        env.globals["project_name"] = self.project_name
        env.globals["model"] = self
        return env

    def get_filepath(self) -> Path:
        """Public method to return the constructed filepath."""
        return self._build_filepath()

    def _build_filepath(self) -> Path:
        """Private helper to construct the dbt asset file path."""
        file_type = self._get_file_type()
        filename = (
            f"{self.filename}.{file_type}"
            if self._get_file_type() == "yml" or self.asset_type == "macro"
            else f"{self.project_name}_{self.filename}.{file_type}"
        )
        return self.project_path / self.asset_subpath / filename

    def _get_file_type(self) -> FileTypeLiteral:
        """Returns the file extension based on asset type."""
        if self.asset_type in ["model", "macro"]:
            return "sql"
        elif self.asset_type == "yml":
            return "yml"
        else:
            raise ValueError(f"Invalid asset type: {self.asset_type}")

    def _get_template(self, env: Environment) -> Template:
        """Get and validate the template exists."""
        template_name = f"{self.filename}.j2"
        try:
            return env.get_template(template_name)
        except Exception as e:
            raise ValueError(f"Failed to load template {template_name}: {str(e)}")

    def generate_asset(self, update: bool, context: dict[str, Any]) -> None:
        """
        Generate a dbt asset using Jinja templating.

        Args:
            update: Whether to update existing files
            context: Template context data for rendering

        Raises:
            ValueError: If template loading or rendering fails
            FileNotFoundError: If template directory is not found
        """
        env = self._jinja_environment()
        template = self._get_template(env)

        try:
            rendered_content = template.render(**context)
            filepath = self.get_filepath()
            filepath.parent.mkdir(parents=True, exist_ok=True)
            write_file(filepath, rendered_content)
            logger.info(f"📄 {self.asset_type.capitalize()}: {self.filename} generated")
        except Exception as e:
            raise ValueError(f"Failed to generate asset {self.filename}: {str(e)}")
