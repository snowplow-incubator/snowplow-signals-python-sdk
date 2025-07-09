# **Testing the Batch Engine (dbt autogen)**

## **Overview**

The Snowplow Signals SDK includes functionality to create auto-generated dbt models that work together to create batch attributes defined in the API efficiently through incremental data processing. The models work with three layers of aggregations: `filtered events` / `daily aggregations` and finally the drop and recompute `attributes` table.

`Batch attributes` are attributes that can't be computed in stream as the period spans over the length of the current session, they will typically involve attributes that you compute over the lifetime of a user or in the last x days as a period.

There are different ways to test this implementation locally during a dev process as per different stages of development:

1. Testing on an a specific view in the API
2. Testing all the CLI commands at once and run a full refresh of the generated package against a warehouse target
3. Testing the inbuilt integration test for the model logic


2. The `local_testing suite` may be used as the quickest way to test the output of the dbt project and running dbt to see if the compiled output makes sense before running a full integration_test.

## Preparation

### Feature JSON

Currently, there is a test API server to simulate the connection between the API and the SDK. There are example batch attribute view definition (JSON) inside `test/autogen` called `integration_test_view.json` (Snowflake) and `integration_test_view.json` (BigQuery). Feel free to modify it or just leave it as is depending on your test purpose. It should not, however be committed otherwise the automated integration_test github actions will fail.

### **Installing the SDK**

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

Currently, you can test the dbt models using our Snowflake dev1 db and also in BigQuery. You will need to have a target set up with your credentials in this manner:

```yml
snowplow_autogen:
  outputs:
    snowflake:
      account: snowplow
      database: YOUR_DB
      password: YOUR_PASSWORD
      role: YOUR_ROLE
      schema: YOUR_SCHEMA
      threads: 4
      type: snowflake
      user: YOUR_USER # it will work with your email
      warehouse: YOUR_WAREHOUSE
    bigquery:
      keyfile: PATH_TO_YOUR_KEYFILE.json
      method: service-account
      project: YOUR_PROJECT
      schema: YOUR_SCHEMA
      threads: 4
      location: EU
      type: bigquery
  target: snowflake
```

## Testing different implementations

### 1. Testing on a specific view in the API

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
poetry run snowplow-batch-autogen init \
    --api-url=http://localhost:8087 \
    --api-key=YOUR_API_KEY \
    --api-key-id=YOUR_API_KEY_ID \
    --org-id=YOUR_ORG_ID \
    --repo-path=./customer_repo \
    [--project-name=PROJECT_NAME] \
    [--debug]

# Generate dbt models
poetry run snowplow-batch-autogen generate \
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
- `--target-type`: The specific warehouse target to generate dbt projects for (one of `snowflake`, `bigquery`)
- `--project-name`: (Optional) Name of a specific project to initialize/generate
- `--update`: (Optional, for generate only) Whether to update existing files
- `--debug`: (Optional) Enable debug logging

If you want to make use of your .env file to load your variables, wrap it around the command like this:

```sh
poetry run dotenv run snowplow-batch-autogen materialize --view-name ecommerce_transaction_interactions_features --view-version 1
```

You can use the -f flag to specify a different file you have e.g .env.dev:

```sh
# test connection
poetry run dotenv -f .env.dev run snowplow-batch-autogen test-connection --verbose
# initialize dbt project
poetry run dotenv -f .env.dev run snowplow-batch-autogen init --repo-path local_testing --view-name test_batch_view --view-version 1 --verbose
# generate dbt project
poetry run dotenv -f .env.dev run snowplow-batch-autogen generate --repo-path local_testing --project-name test_batch_view_1 --verbose 
# materialize table
poetry run dotenv -f .env.dev run snowplow-batch-autogen materialize --view-name test_batch_view --view-version 1 --repo-path ./local_testing/ --verbose
```

### 2. Testing all the CLI commands at once and run a full refresh of the generated package against a warehouse target

Make sure your latest changes apply in the snapshot. Activate your virtual environment which has dbt installed (unless installed globally). Finally, run the test_dbt.sh script, it will generate the dbt project into `local_testing` using all cli commands, then install the package and runs dbt with full-refresh once:

```sh
poetry run pytest --snapshot-update
source path_to_your_env/bin/activate
bash local_testing/test_dbt.sh -d snowflake
```

Note that depending on which events table you use for test purposes you may need to override the following project vars manually first:

```yml
snowplow__atomic_schema: 'YOUR_BIGQUERY_DATASET_NAME' # if not atomic
snowplow__custom_filter: "collector_tstamp > '2025-01-01'" # in case there needs to be a filter on the table for querying
```

Then just cd into the projects and do the full refresh from there instead:
```sh
cd local_testing/customer_repo_bigquery/ecommerce_transaction_interactions_features_1
dbt run --full-refresh --target bigquery
```

### 3. Testing the inbuilt integration test for the model logic

There are two ways to run the integration tests:

1. **Relying on the automated github actions for a full E2E testing**:

The `integration_tests suite` simulates how a customer would use this in a simplified manner. It allows developers to test the E2E customer usage through a combination of pytest and bash scripts that replicates a real-world setup and usage.

The `github/workflows/integration_tests.yml` script will:

1. Install the SDK in development mode
2. Run the pytest-based integration tests
3. Set up a clean customer repository directory
4. Use the SDK to initialize a dbt project with proper structure
5. Generate dbt models based on the attribute definitions
6. Run the generated dbt models to validate they work correctly


2. **Testing E2E locally**:

```sh
poetry run pytest --snapshot-update
source path_to_your_env/bin/activate
bash integration_tests/test_E2E.sh -d snowflake
```
