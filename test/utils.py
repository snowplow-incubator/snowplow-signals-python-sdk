from datetime import UTC, datetime

MOCK_ORG_ID = "1111-1111-1111-1111-1111"


def utc_timestamp():
    return int(datetime.now(tz=UTC).timestamp())
