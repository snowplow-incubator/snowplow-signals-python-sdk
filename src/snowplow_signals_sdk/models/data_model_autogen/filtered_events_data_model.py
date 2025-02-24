from pydantic import BaseModel
from scripts.generate_dbt_config import DbtConfigGenerator
from jinja2 import Environment, select_autoescape, FileSystemLoader
from pathlib import Path
from utils.utils import write_file
from rich import print
from typing import Optional
import os


class FilteredEventsDataModel(BaseModel):
    """
    The data model class contains the model generation config and all of the data products in the model
    """

    def _jinja_environment(self) -> Environment:
        loader = FileSystemLoader([Path(__file__).parent.parent.parent / "templates"])
        env = Environment(loader=loader, autoescape=select_autoescape())
        env.globals["model"] = self
        return env

    def generate_filtered_events_table(self, update: bool, context: dict) -> None:
        env = self._jinja_environment()
        template = env.get_template("signals_filtered_events_table.j2")
        filepath = Path(
            "dbt_project/models/filtered_events/snowplow_autogen_filtered_events_table.sql"
        )

        if filepath.exists() and not update:
            raise ValueError(
                f"{filepath} already exists. Use flag --update to update Data Model"
            )
        print(":white_check_mark: Generating Filtered Events Model")
        write_file(filepath, template.render(**context))
