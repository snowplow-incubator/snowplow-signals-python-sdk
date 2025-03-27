import re
from pathlib import Path
from typing import Any, Optional


def write_file(file_path: Path, content: Optional[str]) -> None:
    """
    Write string content to a file.
    Creates the file and any necessary directories if they do not exist.

    Args:
        file_path (Path): The path to the file to write to.
        content (str): The content to write to the file.
    """
    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True)

    with open(file_path, "w") as f:
        f.write(content)
