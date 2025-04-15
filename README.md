# Snowplow Signals SDK

The Snowplow Signals SDK is a Python SDK that enables you to interact with the Snowplow Signals Profile API. It provides a simple interface to define, deploy, and retrieve user attributes for personalization.

## Installation

```bash
pip install snowplow-signals
```

## Quickstart

```python
from snowplow_signals import Signals, Attribute, Event, View, session_entity

# Initialize the SDK
signals = Signals(
    api_url="API_URL",
    api_key="API_KEY",
    api_key_id="API_KEY_ID",
    org_id="ORG_ID",
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
view = View(
    name="my_view",
    version=1,
    entity=session_entity,
    attributes=[page_view_count],
)
signals.apply([view])

# Retrieve attributes
response = signals.get_online_attributes(
    source=view,
    identifiers="abc-123",
)
```

## Key Features

- Define attributes based on Snowplow events
- Create views to group related attributes
- Deploy views to the Profile API
- Retrieve real-time user attributes

## Release Process

To make a new release:
1. **Prepare the changelog**: Create a commit (e.g., "Prepare for release") that updates the `CHANGELOG.md` with all notable changes for the new version.
2. **Create a release PR**: Open a pull request to the `main` branch with your changelog and any other release-related changes.
3. **Merge the PR**: Merge the release PR using a merge commit. _Do not use squash or rebase._
4. **Run the Release workflow**: Trigger the "Release" workflow in GitHub Actions to publish the new version to PyPI.