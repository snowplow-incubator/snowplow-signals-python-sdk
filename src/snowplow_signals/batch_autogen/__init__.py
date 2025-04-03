"""Snowplow Signals batch project auto-generation module."""

try:
    from snowplow_signals.batch_autogen.dbt_client import BatchAutogenClient

    __all__ = ["BatchAutogenClient"]
except ImportError as e:
    raise ImportError(
        "The batch project auto-generation requires additional dependencies. "
        "Install them with either:\n"
        "  pip install 'snowplow-signals[dbt]'\n"
        "  poetry install --extras dbt"
    ) from e
