from unittest.mock import MagicMock

import pandas as pd
import pytest

from snowplow_signals.models.dataset import WarehouseTable
from snowplow_signals.models.execution import (
    ExecutionError,
    ExecutionResult,
)


def _make_result(df: pd.DataFrame | None = None, count: int = 42) -> ExecutionResult:
    conn = MagicMock()

    def fake_fetch(sql: str) -> pd.DataFrame:
        if "COUNT(*)" in sql:
            return pd.DataFrame({"cnt": [count]})
        return df if df is not None else pd.DataFrame({"a": [1, 2], "b": [3, 4]})

    conn.fetch_pandas.side_effect = fake_fetch
    table = WarehouseTable(database="db", schema="sch", table="tbl")
    return ExecutionResult(table=table, connection=conn)


def test_execution_result_table():
    result = _make_result()
    assert result.table.database == "db"
    assert result.table.schema_ == "sch"
    assert result.table.table == "tbl"


def test_execution_result_row_count():
    result = _make_result(count=99)
    assert result.row_count == 99


def test_execution_result_to_pandas():
    df = pd.DataFrame({"x": [10, 20]})
    result = _make_result(df=df)
    pd.testing.assert_frame_equal(result.to_pandas(), df)


def test_execution_result_to_pandas_invalid_limit():
    result = _make_result()
    with pytest.raises(ValueError):
        result.to_pandas(limit=-1)


def test_execution_error_attributes():
    table = WarehouseTable(database="db", schema="sch", table="tbl")
    cause = RuntimeError("bad sql")

    err = ExecutionError(failed_stage="attributes", failed_table=table, cause=cause)
    assert err.failed_stage == "attributes"
    assert err.failed_table.table == "tbl"
    assert err.cause is cause
    assert "attributes" in str(err)
