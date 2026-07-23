from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import pandas as pd

if TYPE_CHECKING:
    from .connection import WarehouseConnection
    from .dataset import WarehouseTable


class ExecutionResult:
    """Handle returned after executing a dataset bundle.

    Does not fetch data automatically — call `to_pandas()` to pull rows.
    """

    def __init__(
        self,
        table: WarehouseTable,
        connection: WarehouseConnection,
    ) -> None:
        self._table = table
        self._connection = connection

    @property
    def table(self) -> WarehouseTable:
        return self._table

    @property
    def _fqn(self) -> str:
        parts = [
            v
            for v in [self._table.database, self._table.schema_, self._table.table]
            if v is not None
        ]
        return ".".join(parts)

    @property
    def row_count(self) -> int:
        df = self._connection.fetch_pandas(f"SELECT COUNT(*) AS cnt FROM {self._fqn}")
        value = df.iloc[0, 0]
        return int(str(value))

    def to_pandas(self, limit: int = 10_000) -> pd.DataFrame:
        if not isinstance(limit, int) or limit < 0:
            raise ValueError("limit must be a non-negative integer")
        return self._connection.fetch_pandas(f"SELECT * FROM {self._fqn} LIMIT {limit}")


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
