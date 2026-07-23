import pandas as pd
import pytest

from snowplow_signals.execution.snowflake import SnowflakeConnection


def test_execute_creates_table(snowflake_conn: SnowflakeConnection):
    snowflake_conn.execute(
        "CREATE OR REPLACE TABLE test_db.test_schema.my_table (id INT, name VARCHAR)"
    )
    snowflake_conn.execute(
        "INSERT INTO test_db.test_schema.my_table VALUES (1, 'alice'), (2, 'bob')"
    )
    df = snowflake_conn.fetch_pandas(
        "SELECT * FROM test_db.test_schema.my_table ORDER BY id"
    )
    assert len(df) == 2
    assert list(df.columns) == ["ID", "NAME"]


def test_fetch_pandas_returns_dataframe(snowflake_conn: SnowflakeConnection):
    snowflake_conn.execute("CREATE OR REPLACE TABLE test_db.test_schema.nums (val INT)")
    snowflake_conn.execute(
        "INSERT INTO test_db.test_schema.nums VALUES (10), (20), (30)"
    )
    df = snowflake_conn.fetch_pandas(
        "SELECT val FROM test_db.test_schema.nums ORDER BY val"
    )
    assert isinstance(df, pd.DataFrame)
    assert df["VAL"].tolist() == [10, 20, 30]


def test_execute_raises_on_bad_sql(snowflake_conn: SnowflakeConnection):
    with pytest.raises(Exception):
        snowflake_conn.execute("NOT VALID SQL")
