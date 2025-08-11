import datetime
import json
from pathlib import Path
from typing import Any, Dict, Literal, Protocol, TypeVar

from pydantic import ValidationError

from snowplow_signals.batch_autogen.models.batch_source_config import BatchSourceConfig
from snowplow_signals.batch_autogen.models.model import SQLConditions
from snowplow_signals.batch_autogen.models.modeling_step import FilterCondition
from snowplow_signals.cli_logging import get_logger

logger = get_logger(__name__)

WarehouseType = Literal["snowflake", "bigquery"]


def write_file(file_path: Path, content: str) -> None:
    """
    Write string content to a file.
    Creates the file and any necessary directories if they do not exist.
    Args:
        file_path (Path): The path to the file to write to.
        content (Optional[str]): The content to write to the file.
    """
    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True)
    with open(file_path, "w") as f:
        f.write(content)


class VersionedModel(Protocol):
    name: str
    version: Any


T = TypeVar("T", bound=VersionedModel)


def filter_latest_model_version_by_name(data: list[T]) -> list[T]:
    latest_versions: Dict[str, T] = {}
    for item in data:
        name = item.name
        version = item.version
        if name not in latest_versions or version > latest_versions[name].version:
            latest_versions[name] = item
    return list(latest_versions.values())


def timedelta_isoformat(td: datetime.timedelta) -> str:
    minutes, seconds = divmod(td.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{'-' if td.days < 0 else ''}P{abs(td.days)}DT{hours:d}H{minutes:d}M{seconds:d}.{td.microseconds:06d}S"


def batch_source_from_path(config_path: str, table_name: str) -> BatchSourceConfig:
    try:
        with open(config_path) as f:
            data = json.load(f)
        return BatchSourceConfig(**data)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"❌ Error loading batch source config: {str(e)}")
        raise
    except ValidationError as e:
        logger.error(f"❌ Config validation error for {table_name}:\n{e}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error for {table_name}: {e}")
        raise


def get_condition_sql(
    conditions: list[FilterCondition], condition_type: SQLConditions
) -> str:
    condition_sql_list = []
    for condition in conditions:
        operator = condition.operator
        property_name = condition.property
        value = condition.value
        if operator in ["<", ">", "<=", ">="] and isinstance(value, str):
            raise ValueError(
                f"Cannot apply comparison operator '{operator}' on a string value: '{value}'."
            )
        if operator in ["=", "!=", "<", ">", "<=", ">="]:
            value_formatted = f"'{value}'" if isinstance(value, str) else value
            if operator == "!=":
                condition_sql = f" ({property_name} {operator} {value_formatted} or {property_name} is null)"
            else:
                condition_sql = f" {property_name} {operator} {value_formatted}"
        elif operator == "like":
            condition_sql = f" {property_name} LIKE '%{value}%'"
        elif operator == "in":
            condition_sql = f" {property_name} IN({value})"
        else:
            raise ValueError(f"Unsupported operator: {operator}")
        if condition_sql == "":
            raise ValueError(f"Filter condition missing for condition: {condition}")
        condition_sql_list.append(condition_sql)
    return f" {condition_type} ".join(condition_sql_list)
