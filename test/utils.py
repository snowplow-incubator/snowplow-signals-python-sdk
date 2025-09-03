from datetime import UTC, datetime

MOCK_ORG_ID = "1111-1111-1111-1111-1111"
MOCK_API_URL = "http://localhost:8087"
MOCK_API_KEY = "test-api-key"
MOCK_API_KEY_ID = "test-key-id"
MOCK_ATTRIBUTE_GROUP_NAME = "test_view"
MOCK_ATTRIBUTE_GROUP_VERSION = 1


def utc_timestamp() -> int:
    return int(datetime.now(tz=UTC).timestamp())
