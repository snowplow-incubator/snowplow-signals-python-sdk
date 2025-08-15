# Snowplow Signals SDK

The Snowplow Signals SDK is a Python SDK that enables you to interact with the Snowplow Signals Profile API. It provides a simple interface to define, deploy, and retrieve user attributes for personalization.

## Installation

```bash
pip install snowplow-signals
```

## Quickstart

```python
from snowplow_signals import Signals, Attribute, Event, View, domain_sessionid

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
view = StreamView(
    name="my_view",
    version=1,
    entity=domain_sessionid,
    attributes=[page_view_count],
)
signals.apply([view])

# Retrieve attributes
response = signals.get_view_attributes(
    name="my_view",
    version=1,
    entity="domain_sessionid",
    attributes=["page_view_count"],
    identifier="abc-123",
)
```

## Key Features

- Define attributes based on Snowplow events
- Create views to group related attributes
- Deploy views to the Profile API
- Retrieve real-time user attributes

### DBT Project Generation

The SDK includes functionality to automatically generate DBT projects for Snowplow data. This makes it easy to set up and maintain DBT projects that work with Snowplow data.

#### Using the SDK

```python
from snowplow_signals import Signals

# Initialize the signals client
signals = Signals(api_url="https://your-api-url.com")

# Initialize a DBT project
signals.batch_autogen.init_project(
    repo_path="path/to/your/repo",
    target_type="snowflake" # or bigquery
    project_name="your_project_name"  # Optional
)

# Generate DBT models
signals.batch_autogen.generate_models(
    repo_path="path/to/your/repo",
    target_type="snowflake" # or bigquery
    project_name="your_project_name",  # Optional
    update=True  # Whether to update existing files
)
```

#### Using the Command Line

The SDK also includes a command-line interface for DBT project generation. To make your workflow smoother, you can set up your API credentials as environment variables. This way, you won't need to type them in every command:

```bash
export SNOWPLOW_API_URL="YOUR_API_URL"
export SNOWPLOW_API_KEY="YOUR_API_KEY"
export SNOWPLOW_API_KEY_ID="YOUR_API_KEY_ID"
export SNOWPLOW_ORG_ID="YOUR_ORG_ID"
export SNOWPLOW_REPO_PATH="./my_snowplow_repo"
```

```bash
# Initialize a DBT project
snowplow-batch-autogen init --repo-path=path/to/your/repo --target-type=snowflake [--project-name=your_project_name]

# Generate DBT models
snowplow-batch-autogen generate --repo-path=path/to/your/repo --target-type=bigquery [--project-name=your_project_name] [--update]
```

