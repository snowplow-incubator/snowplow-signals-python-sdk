from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

import pandas as pd

if TYPE_CHECKING:
    from .dataset import WarehouseTable


@dataclass
class StageResult:
    stage: Literal["anchors", "attributes", "dataset"]
    table: WarehouseTable
    status: Literal["completed", "failed"]


@dataclass
class ExecutionResult:
    dataframe: pd.DataFrame
    stages: list[StageResult]


class ExecutionError(Exception):
    def __init__(
        self,
        failed_stage: StageResult,
        completed_stages: list[StageResult],
        cause: Exception,
    ):
        self.failed_stage = failed_stage
        self.completed_stages = completed_stages
        self.cause = cause
        super().__init__(
            f"Execution failed at {failed_stage.stage} stage "
            f"(table: {failed_stage.table.table}): {cause}"
        )
