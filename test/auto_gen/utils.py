"""
Utility functions for testing the auto-generation functionality.
Provides mock data and helper functions for testing.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

# Mock data for testing
MOCK_ECOMMERCE_VIEW = {
    "name": "ecommerce_transaction_interactions_features",
    "version": 1,
    "entity": {"name": "user"},
    "ttl": None,
    "batch_source": {
        "name": "ecommerce_transaction_interactions_source",
        "timestamp_field": "UPDATED_AT",
        "created_timestamp_column": None,
        "description": None,
        "tags": None,
        "owner": None,
        "date_partition_column": None,
        "database": "SNOWPLOW_DEV1",
        "schema": None,
        "table": "SNOWPLOW_ECOMMERCE_TRANSACTION_INTERACTIONS_FEATURES",
    },
    "online": True,
    "description": None,
    "tags": None,
    "owner": None,
    "fields": [
        {
            "name": "TOTAL_TRANSACTIONS",
            "description": None,
            "type": "int32",
            "tags": None,
        },
        {
            "name": "TOTAL_REVENUE",
            "description": None,
            "type": "int32",
            "tags": None,
        },
        {
            "name": "AVG_TRANSACTION_REVENUE",
            "description": None,
            "type": "int32",
            "tags": None,
        },
    ],
    "attributes": [],
    "feast_name": "ecommerce_transaction_interactions_features_v1",
    "offline": True,
    "stream_source_name": "ecommerce_transaction_interactions_features_stream",
    "entity_key": "user",
    "view_or_entity_ttl": None,
}

MOCK_USERS_VIEW = {
    "name": "unified_users_features",
    "version": 1,
    "entity": {"name": "user"},
    "ttl": None,
    "batch_source": {
        "name": "snowplow_unified_users_source",
        "timestamp_field": "UPDATED_AT",
        "created_timestamp_column": None,
        "description": None,
        "tags": None,
        "owner": None,
        "date_partition_column": None,
        "database": "SNOWPLOW_DEV1",
        "schema": None,
        "table": "SNOWPLOW_UNIFIED_USERS_FEATURES",
    },
    "online": True,
    "description": None,
    "tags": None,
    "owner": None,
    "fields": [
        {"name": "DAYS_ACTIVE", "description": None, "type": "int32", "tags": None},
        {
            "name": "ACTIVE_TIME_IN_SECONDS",
            "description": None,
            "type": "int32",
            "tags": None,
        },
        {
            "name": "AVG_SESSION_DURATION",
            "description": None,
            "type": "int32",
            "tags": None,
        },
    ],
    "attributes": [],
    "feast_name": "unified_users_features_v1",
    "offline": True,
    "stream_source_name": "unified_users_features_stream",
    "entity_key": "user",
    "view_or_entity_ttl": None,
}

MOCK_ATTRIBUTE_VIEWS = [MOCK_ECOMMERCE_VIEW, MOCK_USERS_VIEW]


def get_attribute_view_response() -> List[Dict[str, Any]]:
    """
    Returns the mock attribute views data.

    Returns:
        List[Dict[str, Any]]: List of mock attribute view configurations
    """
    return MOCK_ATTRIBUTE_VIEWS


def get_attribute_view_response_from_file() -> List[Dict[str, Any]]:
    """
    Reads and returns mock attribute views from a JSON file.

    Returns:
        List[Dict[str, Any]]: List of mock attribute view configurations from file

    Raises:
        FileNotFoundError: If the mock data file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    json_path = Path(__file__).parent / "mock_attribute_views.json"
    with open(json_path, "r") as f:
        data = json.load(f)
    return data["mock_attribute_views"]
