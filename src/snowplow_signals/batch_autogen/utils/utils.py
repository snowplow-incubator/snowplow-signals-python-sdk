import datetime
from pathlib import Path
from typing import Dict, Any, Protocol, TypeVar
import json
from snowplow_signals.logging import get_logger

logger = get_logger(__name__)


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


def load_config_from_path(config_path: str, table_name: str) -> Dict[str, Any]:
    try:
        with open(config_path) as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"❌ Error loading config for {table_name}: {e}")
        raise
