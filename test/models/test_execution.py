import pandas as pd
import pytest

from snowplow_signals.models.dataset import WarehouseTable
from snowplow_signals.models.execution import (
    ExecutionError,
    ExecutionResult,
)


def test_execution_result_dataframe():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    result = ExecutionResult(dataframe=df)
    pd.testing.assert_frame_equal(result.dataframe, df)


def test_execution_error_attributes():
    table = WarehouseTable(database="db", schema="sch", table="tbl")
    cause = RuntimeError("bad sql")

    err = ExecutionError(failed_stage="attributes", failed_table=table, cause=cause)
    assert err.failed_stage == "attributes"
    assert err.failed_table.table == "tbl"
    assert err.cause is cause
    assert "attributes" in str(err)
