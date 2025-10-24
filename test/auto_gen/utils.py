"""
Utility functions for testing the auto-generation functionality.
Provides mock data and helper functions for testing.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Literal

# Mock data for testing
MOCK_ECOMMERCE_VIEW = {
    "name": "ecommerce_transaction_interactions_features",
    "version": 1,
    "attribute_key": {"name": "user", "key": "user"},
    "ttl": None,
    "batch_source": {
        "name": "ecommerce_transaction_interactions_source",
        "timestamp_field": "UPDATED_AT",
        "description": None,
        "owner": None,
        "date_partition_column": None,
        "database": "SNOWPLOW_DEV1",
        "schema": "DUMMY_SCHEMA",
        "table": "SNOWPLOW_ECOMMERCE_TRANSACTION_INTERACTIONS_FEATURES",
    },
    "online": True,
    "description": None,
    "owner": None,
    "fields": [
        {
            "name": "TOTAL_TRANSACTIONS",
            "description": None,
            "type": "int32",
        },
        {
            "name": "TOTAL_REVENUE",
            "description": None,
            "type": "int32",
        },
        {
            "name": "AVG_TRANSACTION_REVENUE",
            "description": None,
            "type": "int32",
        },
    ],
    "attributes": [],
    "feast_name": "ecommerce_transaction_interactions_features_v1",
    "offline": True,
    "stream_source_name": "ecommerce_transaction_interactions_features_stream",
    "attribute_key_or_name": "user",
    "attribute_group_or_attribute_key_ttl": None,
    "full_name": "ecommerce_transaction_interactions_features_v1",
}

MOCK_USERS_VIEW = {
    "name": "unified_users_features",
    "version": 1,
    "attribute_key": {"name": "user"},
    "ttl": None,
    "batch_source": {
        "name": "snowplow_unified_users_source",
        "timestamp_field": "UPDATED_AT",
        "description": None,
        "owner": None,
        "date_partition_column": None,
        "database": "SNOWPLOW_DEV1",
        "schema": "DUMMY_SCHEMA",
        "table": "SNOWPLOW_UNIFIED_USERS_FEATURES",
    },
    "online": True,
    "description": None,
    "owner": None,
    "fields": [
        {"name": "DAYS_ACTIVE", "description": None, "type": "int32"},
        {
            "name": "ACTIVE_TIME_IN_SECONDS",
            "description": None,
            "type": "int32",
        },
        {
            "name": "AVG_SESSION_DURATION",
            "description": None,
            "type": "int32",
        },
    ],
    "attributes": [],
    "feast_name": "unified_users_features_v1",
    "offline": True,
    "stream_source_name": "unified_users_features_stream",
    "attribute_key_or_name": "user",
    "attribute_group_or_attribute_key_ttl": None,
    "full_name": "unified_users_features_v1",
}

MOCK_ATTRIBUTE_VIEWS = [MOCK_ECOMMERCE_VIEW, MOCK_USERS_VIEW]


def get_attribute_view_response() -> List[Dict[str, Any]]:
    """
    Returns the mock attribute groups data.

    Returns:
        List[Dict[str, Any]]: List of mock attribute group configurations
    """
    return MOCK_ATTRIBUTE_VIEWS


def get_attribute_view_response_from_file() -> List[Dict[str, Any]]:
    """
    Reads and returns mock attribute groups from a JSON file.

    Returns:
        List[Dict[str, Any]]: List of mock attribute group configurations from file

    Raises:
        FileNotFoundError: If the mock data file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    json_path = Path(__file__).parent / "mock_attribute_views_snowflake.json"
    with open(json_path, "r") as f:
        data = json.load(f)
    return data["mock_attribute_views"]


def get_integration_test_view_response(
    warehouse: Literal["snowflake", "bigquery", "databricks"],
) -> List[Dict[str, Any]]:
    """
    Reads and returns mock attribute groups from a JSON file.

    Returns:
        List[Dict[str, Any]]: List of mock attribute group configurations from file

    Raises:
        FileNotFoundError: If the mock data file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    if warehouse == "snowflake":
        json_path = Path(__file__).parent / "integration_test_view_snowflake.json"
    elif warehouse == "bigquery":
        json_path = Path(__file__).parent / "integration_test_view_bigquery.json"
    elif warehouse == "databricks":
        json_path = Path(__file__).parent / "integration_test_view_databricks.json"
    else:
        raise ValueError(f"Unsupported warehouse: {warehouse}")
    with open(json_path, "r") as f:
        data = json.load(f)
    return data["mock_attribute_views"]
