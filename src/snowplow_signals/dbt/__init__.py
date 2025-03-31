"""Snowplow Signals dbt integration module."""

try:
    from snowplow_signals.dbt.cli import app
    from snowplow_signals.dbt.dbt_client import DbtClient

    __all__ = ["app", "DbtClient"]
except ImportError as e:
    raise ImportError(
        "The dbt integration requires additional dependencies. "
        "Install them with either:\n"
        "  pip install 'snowplow-signals[dbt]'\n"
        "  poetry install --with dbt"
    ) from e 