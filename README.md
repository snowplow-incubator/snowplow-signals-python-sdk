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

## Key Features

- Define attributes based on Snowplow events
- Create attribute groups for related attributes
- Deploy attribute groups to the Profile API
- Retrieve real-time user attributes
