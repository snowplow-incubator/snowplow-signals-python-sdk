from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from snowplow_signals import AttributeGroup, Criteria, Criterion, domain_userid
from snowplow_signals.dataset_client import DatasetClient
from snowplow_signals.execution.snowflake import SnowflakeConnection
from snowplow_signals.models import AtomicProperty, SessionAnchors, TrainingSpan
from snowplow_signals.models.dataset import DatasetBundle
from snowplow_signals.models.execution import ExecutionError, ExecutionResult
from snowplow_signals.models.model import (
    AttributeKeyOutput,
    AttributeSqlFile,
    DatasetAttributeGroups,
    DatasetBundleRequest,
    DatasetBundleResponse,
    DatasetSqlFile,
)


def _make_request(
    attribute_group_name: str = "test_group",
) -> DatasetBundleRequest:
    return DatasetBundleRequest(
        anchors=SessionAnchors(
            goal_criteria=Criteria(
                any=[Criterion.eq(AtomicProperty(name="se_action"), "purchase")]
            ),
            training_span=TrainingSpan(
                start_time=datetime(2025, 1, 1, tzinfo=timezone.utc),
                end_time=datetime(2025, 6, 1, tzinfo=timezone.utc),
            ),
        ),
        attributes=DatasetAttributeGroups(
            attribute_groups=[
                AttributeGroup(
                    name=attribute_group_name,
                    attribute_key=domain_userid,
                    owner="test@example.com",
                )
            ],
        ),
    )


def _make_bundle(
    anchors_sql: str,
    attributes_sql: list[tuple[str, str]],
    dataset_sql: str,
) -> DatasetBundle:
    """Build a DatasetBundle with controlled response.

    Args:
        anchors_sql: SQL for the anchors stage.
        attributes_sql: List of (table_name, sql) for each attribute stage.
        dataset_sql: SQL for the dataset stage.
    """
    response = DatasetBundleResponse(
        anchors=DatasetSqlFile(
            database="test_db",
            schema="test_schema",
            table="signals_anchors",
            sql=anchors_sql,
        ),
        attributes=[
            AttributeSqlFile(
                database="test_db",
                schema="test_schema",
                table=table_name,
                sql=sql,
                attribute_key=AttributeKeyOutput(name=table_name, blobl_path=None),
            )
            for table_name, sql in attributes_sql
        ],
        dataset=DatasetSqlFile(
            database="test_db",
            schema="test_schema",
            table="signals_training_dataset",
            sql=dataset_sql,
        ),
    )
    client = DatasetClient(api_client=MagicMock())
    return DatasetBundle(
        request=_make_request(), response=response, dataset_client=client
    )


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

    assert result.table.database == "test_db"
    assert result.table.schema_ == "test_schema"
    assert result.table.table == "signals_training_dataset"
    assert result.row_count == 1

    df = result.to_pandas()
    assert len(df) == 1
    assert set(df.columns) == {"USER_ID", "LABEL", "PAGE_VIEWS"}
    assert df["USER_ID"].iloc[0] == 1
    assert df["PAGE_VIEWS"].iloc[0] == 42


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
    assert err.failed_stage == "attributes"
    assert err.failed_table.table == "signals_attr_bad"


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
    assert err.failed_stage == "anchors"
