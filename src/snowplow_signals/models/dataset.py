from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

from .criteria_wrapper import Criteria
from .model import Output as OutputModel
from .model import SessionAnchors as SessionAnchorsModel


class SessionAnchors(SessionAnchorsModel):
    """SDK wrapper that uses the Criteria wrapper for goal_criteria."""

    model_config = ConfigDict(populate_by_name=True)
    goal_criteria: Criteria  # type: ignore[override]


class Output(OutputModel):
    """SDK wrapper with populate_by_name enabled."""

    model_config = ConfigDict(populate_by_name=True)


class DatasetBundle(BaseModel):
    files: dict[str, str]

    def save_to(self, path: str | Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        for filename, content in self.files.items():
            (path / filename).write_text(content)
