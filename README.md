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
- Build training datasets with session-based or custom anchors
- Execute dataset builds server-side and preview results

## Dataset Builder

Build training datasets from your Snowplow events using the dataset builder. You can generate SQL bundles locally or submit dataset builds for server-side execution.

### Generate SQL bundle

```python
from datetime import datetime, timezone
from snowplow_signals import Signals, Criteria, Criterion, TrainingSpan
from snowplow_signals.models import AtomicProperty

bundle = signals.build_dataset_with_session_anchors(
    attribute_groups=[my_attribute_group],
    goal_criteria=Criteria(
        any=[Criterion.eq(AtomicProperty(name="se_action"), "purchase")]
    ),
    training_span=TrainingSpan(
        start_time=datetime(2025, 1, 1, tzinfo=timezone.utc),
        end_time=datetime(2025, 6, 1, tzinfo=timezone.utc),
    ),
)

# Save SQL files to disk
bundle.save_to("./dataset_output")
```

### Server-side execution

Submit a dataset build for execution on your warehouse and poll for results:

```python
import time
from snowplow_signals import DatasetRunStatus

run = signals.submit_dataset_run_with_session_anchors(
    attribute_groups=[my_attribute_group],
    goal_criteria=Criteria(
        any=[Criterion.eq(AtomicProperty(name="se_action"), "purchase")]
    ),
    training_span=TrainingSpan(
        start_time=datetime(2025, 1, 1, tzinfo=timezone.utc),
        end_time=datetime(2025, 6, 1, tzinfo=timezone.utc),
    ),
)

# Poll for completion
while True:
    status = signals.get_dataset_run_status(run.id)
    if status.status != DatasetRunStatus.PENDING:
        break
    time.sleep(5)

# Preview results
if status.status == DatasetRunStatus.SUCCESS:
    preview = signals.get_dataset_run_preview(run.id, limit=100)
    df = preview.to_pandas()
    print(df)
```
