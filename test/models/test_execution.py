import pandas as pd
import pytest

from snowplow_signals.models.dataset import WarehouseTable
from snowplow_signals.models.execution import (
    ExecutionError,
    ExecutionResult,
    StageResult,
)


def test_stage_result_creation():
    table = WarehouseTable(database="db", schema="sch", table="tbl")
    stage = StageResult(stage="anchors", table=table, status="completed")
    assert stage.stage == "anchors"
    assert stage.table.table == "tbl"
    assert stage.status == "completed"


def test_execution_result_to_pandas():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    table = WarehouseTable(database="db", schema="sch", table="tbl")
    result = ExecutionResult(
        dataframe=df,
        stages=[StageResult(stage="anchors", table=table, status="completed")],
    )
    pd.testing.assert_frame_equal(result.to_pandas(), df)


def test_execution_error_attributes():
    table = WarehouseTable(database="db", schema="sch", table="tbl")
    failed = StageResult(stage="attributes", table=table, status="failed")
    completed = [StageResult(stage="anchors", table=table, status="completed")]
    cause = RuntimeError("bad sql")

    err = ExecutionError(failed_stage=failed, completed_stages=completed, cause=cause)
    assert err.failed_stage.stage == "attributes"
    assert len(err.completed_stages) == 1
    assert err.cause is cause
    assert "attributes" in str(err)
