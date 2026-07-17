from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

import pandas as pd

if TYPE_CHECKING:
    from .dataset import WarehouseTable


@dataclass
class ExecutionResult:
    dataframe: pd.DataFrame


class ExecutionError(Exception):
    def __init__(
        self,
        failed_stage: Literal["anchors", "attributes", "dataset"],
        failed_table: WarehouseTable,
        cause: Exception,
    ):
        self.failed_stage = failed_stage
        self.failed_table = failed_table
        self.cause = cause
        super().__init__(
            f"Execution failed at {failed_stage} stage "
            f"(table: {failed_table.table}): {cause}"
        )
