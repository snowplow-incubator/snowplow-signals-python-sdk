import pytest

from snowplow_signals.execution.snowflake import SnowflakeConnection
from snowplow_signals.models.dataset import DatasetBundle
from snowplow_signals.models.execution import ExecutionError


def _make_bundle(
    anchors_sql: str,
    attributes_sql: list[tuple[str, str]],
    dataset_sql: str,
) -> DatasetBundle:
    """Build a DatasetBundle with controlled response_data.

    Args:
        anchors_sql: SQL for the anchors stage.
        attributes_sql: List of (table_name, sql) for each attribute stage.
        dataset_sql: SQL for the dataset stage.
    """
    files = {}
    response_data = {
        "anchors": {
            "database": "test_db",
            "schema": "test_schema",
            "table": "signals_anchors",
            "sql": anchors_sql,
        },
        "attributes": [
            {
                "database": "test_db",
                "schema": "test_schema",
                "table": table_name,
                "sql": sql,
            }
            for table_name, sql in attributes_sql
        ],
        "dataset": {
            "database": "test_db",
            "schema": "test_schema",
            "table": "signals_training_dataset",
            "sql": dataset_sql,
        },
    }
    # Populate files dict (mirrors what dataset_client does)
    files["signals_anchors.sql"] = anchors_sql
    for table_name, sql in attributes_sql:
        files[f"{table_name}.sql"] = sql
    files["signals_training_dataset.sql"] = dataset_sql
    return DatasetBundle(files=files, response_data=response_data)


def test_execute_happy_path(snowflake_conn: SnowflakeConnection):
    bundle = _make_bundle(
        anchors_sql=(
            "CREATE OR REPLACE TABLE test_db.test_schema.signals_anchors "
            "AS SELECT 1 AS user_id, 'pos' AS label"
        ),
        attributes_sql=[
            (
                "signals_attr_page_views",
                "CREATE OR REPLACE TABLE test_db.test_schema.signals_attr_page_views "
                "AS SELECT 1 AS user_id, 42 AS page_views",
            ),
        ],
        dataset_sql=(
            "CREATE OR REPLACE TABLE test_db.test_schema.signals_training_dataset "
            "AS SELECT a.user_id, a.label, attr.page_views "
            "FROM test_db.test_schema.signals_anchors a "
            "JOIN test_db.test_schema.signals_attr_page_views attr "
            "ON a.user_id = attr.user_id"
        ),
    )

    result = bundle.execute(snowflake_conn)

    df = result.to_pandas()
    assert len(df) == 1
    assert set(df.columns) == {"USER_ID", "LABEL", "PAGE_VIEWS"}
    assert df["USER_ID"].iloc[0] == 1
    assert df["PAGE_VIEWS"].iloc[0] == 42


def test_execute_stages_metadata(snowflake_conn: SnowflakeConnection):
    bundle = _make_bundle(
        anchors_sql=(
            "CREATE OR REPLACE TABLE test_db.test_schema.signals_anchors "
            "AS SELECT 1 AS id"
        ),
        attributes_sql=[
            (
                "signals_attr_a",
                "CREATE OR REPLACE TABLE test_db.test_schema.signals_attr_a "
                "AS SELECT 1 AS id, 10 AS val",
            ),
            (
                "signals_attr_b",
                "CREATE OR REPLACE TABLE test_db.test_schema.signals_attr_b "
                "AS SELECT 1 AS id, 20 AS val",
            ),
        ],
        dataset_sql=(
            "CREATE OR REPLACE TABLE test_db.test_schema.signals_training_dataset "
            "AS SELECT 1 AS id"
        ),
    )

    result = bundle.execute(snowflake_conn)

    assert len(result.stages) == 4  # anchors + 2 attributes + dataset
    assert all(s.status == "completed" for s in result.stages)
    assert result.stages[0].stage == "anchors"
    assert result.stages[0].table.table == "signals_anchors"
    assert result.stages[1].stage == "attributes"
    assert result.stages[2].stage == "attributes"
    assert result.stages[3].stage == "dataset"
    assert result.stages[3].table.table == "signals_training_dataset"


def test_execute_error_reports_failed_stage(snowflake_conn: SnowflakeConnection):
    bundle = _make_bundle(
        anchors_sql=(
            "CREATE OR REPLACE TABLE test_db.test_schema.signals_anchors "
            "AS SELECT 1 AS id"
        ),
        attributes_sql=[
            (
                "signals_attr_bad",
                "THIS IS NOT VALID SQL",
            ),
        ],
        dataset_sql=(
            "CREATE OR REPLACE TABLE test_db.test_schema.signals_training_dataset "
            "AS SELECT 1 AS id"
        ),
    )

    with pytest.raises(ExecutionError) as exc_info:
        bundle.execute(snowflake_conn)

    err = exc_info.value
    assert err.failed_stage.stage == "attributes"
    assert err.failed_stage.table.table == "signals_attr_bad"
    assert err.failed_stage.status == "failed"
    assert len(err.completed_stages) == 1
    assert err.completed_stages[0].stage == "anchors"
    assert err.completed_stages[0].status == "completed"


def test_execute_error_on_first_stage(snowflake_conn: SnowflakeConnection):
    bundle = _make_bundle(
        anchors_sql="THIS IS NOT VALID SQL",
        attributes_sql=[],
        dataset_sql=(
            "CREATE OR REPLACE TABLE test_db.test_schema.signals_training_dataset "
            "AS SELECT 1 AS id"
        ),
    )

    with pytest.raises(ExecutionError) as exc_info:
        bundle.execute(snowflake_conn)

    err = exc_info.value
    assert err.failed_stage.stage == "anchors"
    assert len(err.completed_stages) == 0
