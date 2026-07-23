from __future__ import annotations

import pandas as pd
from snowflake.connector import SnowflakeConnection as _SnowflakeConnection


class SnowflakeConnection:
    """Wraps a raw snowflake.connector.Connection to satisfy WarehouseConnection."""

    def __init__(self, connection: _SnowflakeConnection):
        self._conn = connection

    def execute(self, sql: str) -> None:
        cursor = self._conn.cursor()
        try:
            cursor.execute(sql)
        finally:
            cursor.close()

    def fetch_pandas(self, sql: str) -> pd.DataFrame:
        cursor = self._conn.cursor()
        try:
            cursor.execute(sql)
            return cursor.fetch_pandas_all()
        finally:
            cursor.close()
