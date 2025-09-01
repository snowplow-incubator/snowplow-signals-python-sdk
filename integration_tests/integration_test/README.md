# snowplow-batch-engine-integration-tests

Integration test suite for batch autogen dbt models.

To test locally, run this script from the root to create the repo:
```bash
poetry run python integration_tests/replicate_files.py test/auto_gen/__snapshots__/test_snapshots_snowflake.ambr integration_tests
```

Then copy the integration_test folder over to this repo and cd into it and install the package:

```bash
cd integration_tests/ecommerce_transaction_interactions_features_1/integration_test
dbt deps
```

Finally, run the scripts using:

```bash
bash .scripts/integration_test.sh -d {warehouse}
```

Supported warehouses (should be the same as your target in your profile.yml):

- snowflake
- bigquery
- all (iterates through all supported warehouses)

Good to know:
- the dataset contains a duplicate event where the data is loaded on a different day which we don't handle now and it is part of the first run, so it will not cause issues (we are taking the first loaded event)
- there is one row that is filtered because it happened earlier than the start_tstamp
