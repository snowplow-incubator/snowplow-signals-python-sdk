# **Integration Tests**

## **Overview**

The Snowplow Signals SDK includes functionality to create auto-generated dbt models that work together to create batch attributes defined in the API efficiently through incremental data processing. The models work with three layers of aggregations: `filtered events` / `daily aggregations` and finally the drop and recompute `attributes` table.

`Batch attributes` are attributes that can't be computed in stream as the period spans over the length of the current session, they will typically involve attributes that you compute over the lifetime of a user or in the last x days as a period.

The `integration_tests suite` simulates how a customer would use this in a simplified manner. It allows developers to test the E2E customer usage through a combination of pytest and bash scripts that replicates a real-world setup and usage.

## Feature JSON

Currently, there is a test API server to simulate the connection between the API and the SDK. There is an example batch attribute view definition (JSON) inside `local_testing/static_signals_config_offline.json`. Feel free to modify it or just leave it as is.

## How to use this?

### **Install the SDK**

The integration test will automatically install the SDK in development mode, but if you want to do it manually:

```sh
# From the project root
poetry install
```

This will make the `snowplow_signals` module available in your Python environment with all the dbt functionality included.

### Install test dependencies

Make sure the test dependencies are installed:

```sh
poetry install --with dev
```

### Prepare your dbt target

Currently you can test the dbt models using our Snowflake dev1 db. You will need to have a target set up with your credentials in this manner:

```yml
snowplow_autogen:
  outputs:
    snowflake:
      account: snowplow
      database: YOUR_DB
      password: YOUR_PASSWORD
      role: YOUR_ROLE
      schema: signals
      threads: 4
      type: snowflake
      user: YOUR_USER # it will work with your email
      warehouse: YOUR_WAREHOUSE
  target: snowflake
```

### Running the Integration Tests

There are two ways to run the integration tests:

1. **Using pytest directly**:

```sh
# From the project root
poetry run pytest test/auto_gen/test_e2e_batch_autogen.py -v
```

2. **Using the integration test script**:

```sh
# From the project root
bash integration_tests/test_dbt.sh
```

The integration test script will:

1. Install the SDK in development mode
2. Run the pytest-based integration tests
3. Set up a clean customer repository directory
4. Use the SDK to initialize a dbt project with proper structure
5. Generate dbt models based on the attribute definitions
6. Run the generated dbt models to validate they work correctly

### Using the dbt functionality in the SDK

You can use the SDK programmatically in your Python code:

```python
from snowplow_signals.api_client import ApiClient
from snowplow_signals.batch_autogen import BatchAutogenClient

# Initialize the API client
api_client = ApiClient(
    api_url="http://localhost:8087",
    api_key="YOUR_API_KEY",
    api_key_id="YOUR_API_KEY_ID",
    org_id="YOUR_ORG_ID"
)

# Initialize the batch autogen client
batch_autogen_client = BatchAutogenClient(api_client=api_client)

# Initialize a dbt project
batch_autogen_client.init_project(repo_path="./customer_repo")

# Generate dbt models
batch_autogen_client.generate_models(repo_path="./customer_repo", update=True)
```

You can also use the CLI interface (after installing the SDK):

```sh
# Initialize a dbt project
poetry run snowplow-dbt init \
    --api-url=http://localhost:8087 \
    --api-key=YOUR_API_KEY \
    --api-key-id=YOUR_API_KEY_ID \
    --org-id=YOUR_ORG_ID \
    --repo-path=./customer_repo \
    [--project-name=PROJECT_NAME] \
    [--debug]

# Generate dbt models
poetry run snowplow-dbt generate \
    --api-url=http://localhost:8087 \
    --api-key=YOUR_API_KEY \
    --api-key-id=YOUR_API_KEY_ID \
    --org-id=YOUR_ORG_ID \
    --repo-path=./customer_repo \
    [--project-name=PROJECT_NAME] \
    [--update] \
    [--debug]
```

The CLI commands support the following options:

- `--api-url`: URL of the API server to fetch schema information
- `--api-key`: API key for authentication
- `--api-key-id`: ID of the API key
- `--org-id`: Organization ID
- `--repo-path`: Path to the repository where projects will be stored
- `--project-name`: (Optional) Name of a specific project to initialize/generate
- `--update`: (Optional, for generate only) Whether to update existing files
- `--debug`: (Optional) Enable debug logging