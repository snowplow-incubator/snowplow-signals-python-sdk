# Snowplow Signals Python SDK

The Snowplow Signals Python SDK enables you to interact with the Snowplow Signals Profile API. It provides a simple interface to define, deploy, and retrieve user attributes for personalization.

## Installation

```bash
pip install snowplow-signals
```

## Quickstart

```python
from snowplow_signals import Signals, SignalsSandbox, Attribute, Event, StreamAttributeGroup, domain_sessionid

# Initialize the SDK with BDP authentication (default)
signals = Signals(
    api_url="API_URL",
    api_key="API_KEY",
    api_key_id="API_KEY_ID",
    org_id="ORG_ID",
)

# Or initialize with SANDBOX authentication
signals = SignalsSandbox(
    api_url="API_URL",
    sandbox_token="YOUR_SANDBOX_TOKEN",
)

# Define an attribute
page_view_count = Attribute(
    name="page_view_count",
    type="int32",
    events=[
        Event(
            vendor="com.snowplowanalytics.snowplow",
            name="page_view",
            version="1-0-0",
        )
    ],
    aggregation="counter"
)

# Create and deploy a view
stream_attribute_group = StreamAttributeGroup(
    name="my_attribute_group",
    version=1,
    attribute_key=domain_sessionid,
    attributes=[page_view_count],
)
signals.publish([stream_attribute_group])

# Retrieve attributes
response = signals.get_group_attributes(
    name="my_attribute_group",
    version=1,
    attribute_key="domain_sessionid",
    attributes=["page_view_count"],
    identifier="abc-123",
)
```

## Timestamp Granularity

The `granularity` option on an attribute truncates the timestamp property value to the specified
unit (in UTC) before feeding it into the aggregation. This is useful for computing active-day counts
or time-of-day / day-of-week seasonality features.

Valid values: `"second"`, `"minute"`, `"hour"`, `"day"`, `"week"`, `"month"`, `"year"`.

`granularity` is only valid on `unix_timestamp` and `unix_timestamp_list` attribute types. The
output type of the attribute remains `unix_timestamp`.

### Example: count of distinct active days

```python
from snowplow_signals import Signals, Attribute, Event, StreamAttributeGroup, domain_userid

signals = Signals(
    api_url="API_URL",
    api_key="API_KEY",
    api_key_id="API_KEY_ID",
    org_id="ORG_ID",
)

# Count how many distinct calendar days (UTC) the user has been active
active_days = Attribute(
    name="active_days",
    type="unix_timestamp",
    events=[
        Event(
            vendor="com.snowplowanalytics.snowplow",
            name="page_view",
            version="1-0-0",
        )
    ],
    aggregation="approx_count_distinct",
    granularity="day",  # truncate collector_tstamp to day before counting distinct values
)

stream_attribute_group = StreamAttributeGroup(
    name="user_engagement",
    version=1,
    attribute_key=domain_userid,
    owner="team@example.com",
    attributes=[active_days],
)
signals.publish([stream_attribute_group])
```

## Key Features

- Define attributes based on Snowplow events
- Create attribute groups for related attributes
- Deploy attribute groups to the Profile API
- Retrieve real-time user attributes
- Compute date/time granularity aggregations (active-days, seasonality)
