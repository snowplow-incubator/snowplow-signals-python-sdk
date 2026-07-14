from __future__ import annotations

from typing import Protocol

import pandas as pd


class WarehouseConnection(Protocol):
    """Minimal contract for warehouse connections.

    Implement `execute` for DDL/DML and `fetch_pandas` for queries that return data.
    See SnowflakeConnection for a reference implementation.
    """

    def execute(self, sql: str) -> None: ...

    def fetch_pandas(self, sql: str) -> pd.DataFrame: ...
