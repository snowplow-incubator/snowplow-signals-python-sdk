# **Integration Tests**

## **Overview**
The Snowplow Signals SDK includes functionality to create auto-generated dbt models that work together to create batch attributes defined in the API efficiently through incremental data processing. The models work with three layers of aggregations: `filtered events` / `daily aggregations` and finally the drop and recompute `attributes` table. 

`Batch attributes` are attributes that can't be computed in stream as the period spans over the length of the current session, they will typically involve attributes that you compute over the lifetime of a user or in the last x days as a period.

The `integration_tests suite` simulates how a customer would use this in a simplified manner. It allows developers to test the E2E customer usage through a bash script that replicates a real-world setup and usage.

## Feature JSON
Currently, there is a test API server to simulate the connection between the API and the SDK. There is an example batch attribute view definition (JSON) inside `local_testing/static_signals_config_offline.json`. Feel free to modify it or just leave it as is.

## How to use this?

### **Install the SDK**
The integration test will automatically install the SDK in development mode, but if you want to do it manually:

```sh
# From the project root
pip install -e .
```

This will make the `snowplow_signals` module available in your Python environment with all the dbt functionality included.

### Install test dependencies
Make sure the test dependencies are installed:
```sh
pip install -r test/auto_gen/requirements.txt
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

### Run integration_test.sh
This script will:
1. Install the SDK in development mode
2. Start a local API server to simulate the Signals API
3. Set up a clean customer repository directory
4. Use the SDK to initialize a dbt project with proper structure
5. Generate dbt models based on the attribute definitions
6. Run the generated dbt models to validate they work correctly

To run the integration test:

```sh
cd test/auto_gen
bash integration_test.sh
```

### Using the dbt functionality in the SDK

Once the SDK is installed, you can use the dbt functionality in your Python code:

```python
from snowplow_signals import Signals

# Initialize the signals client
signals = Signals(api_url="http://localhost:8087")

# Initialize a dbt project
signals.dbt.init_project(repo_path="./customer_repo")

# Generate dbt models
signals.dbt.generate_models(repo_path="./customer_repo", update=True)
```

You can also use the CLI interface (after installing the SDK):

```sh
# Initialize a dbt project
snowplow-dbt init --repo-path=./customer_repo --api-url=http://localhost:8087

# Generate dbt models
snowplow-dbt generate --repo-path=./customer_repo --update
```
