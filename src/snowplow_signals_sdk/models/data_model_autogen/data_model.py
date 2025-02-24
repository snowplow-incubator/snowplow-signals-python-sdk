from pydantic import BaseModel
from scripts.generate_dbt_config import DbtConfigGenerator
from jinja2 import Environment, select_autoescape, FileSystemLoader
from pathlib import Path
from utils.utils import write_file
from rich import print
from typing import Optional
import os


class DataModel(BaseModel):
    """
    The data model class contains the model generation config.
    """

    def _jinja_environment(self) -> Environment:
        loader = FileSystemLoader([Path(__file__).parent.parent.parent / "templates"])
        env = Environment(loader=loader, autoescape=select_autoescape())
        env.globals["model"] = self
        return env
