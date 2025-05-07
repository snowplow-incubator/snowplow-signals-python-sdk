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
view = View(
    name="my_view",
    version=1,
    entity=domain_sessionid,
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
    project_name="your_project_name"  # Optional
)

# Generate DBT models
signals.batch_autogen.generate_models(
    repo_path="path/to/your/repo",
    project_name="your_project_name",  # Optional
    update=True  # Whether to update existing files
)
```

#### Using the Command Line

The SDK also includes a command-line interface for DBT project generation:

```bash
# Initialize a DBT project
snowplow-dbt init --repo-path=path/to/your/repo [--project-name=your_project_name] [--api-url=https://your-api-url.com]

# Generate DBT models
snowplow-dbt generate --repo-path=path/to/your/repo [--project-name=your_project_name] [--update]
```

