import fakesnow
import pytest

from snowplow_signals.execution.snowflake import SnowflakeConnection


@pytest.fixture
def snowflake_conn():
    with fakesnow.patch():
        import snowflake.connector

        conn = snowflake.connector.connect()
        conn.cursor().execute("CREATE DATABASE test_db")
        conn.cursor().execute("CREATE SCHEMA test_db.test_schema")
        yield SnowflakeConnection(conn)
        conn.close()
