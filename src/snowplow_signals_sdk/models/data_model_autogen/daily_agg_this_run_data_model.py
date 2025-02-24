from pydantic import BaseModel
from scripts.generate_dbt_config import DbtConfigGenerator
from jinja2 import Environment, select_autoescape, FileSystemLoader
from pathlib import Path
from utils.utils import write_file
from rich import print
from typing import Optional
import os
from models.data_model_autogen.data_model import DataModel


class DailyAggThisRunDataModel(DataModel):
    """
    The data model class contains the model generation config for the daily aggregate this run table.
    """

    def generate_daily_agg_this_run_table(self, update: bool, context: dict) -> None:
        env = self._jinja_environment()
        template = env.get_template("snowplow_signals_daily_aggregates_this_run.j2")
        filepath = Path(
            "dbt_project/models/daily_aggregates/snowplow_autogen_daily_aggregates_this_run.sql"
        )

        if filepath.exists() and not update:
            raise ValueError(
                f"{filepath} already exists. Use flag --update to update Data Model"
            )
        print(":white_check_mark: Generating Daily Aggregates This Run Model")
        write_file(filepath, template.render(**context))
