from datetime import UTC, datetime


def utc_timestamp():
    return int(datetime.now(tz=UTC).timestamp())
