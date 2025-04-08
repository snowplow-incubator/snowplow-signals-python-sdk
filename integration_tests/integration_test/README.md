# snowplow-batch-autogen-integration-tests

Integration test suite for batch autogen dbt models.

The `./scripts` directory contains the following:

Run the scripts using:

```bash
bash integration_tests.sh -d {warehouse}
```

Supported warehouses (should be the same as your target in your profile.yml):

- snowflake
- all (iterates through all supported warehouses)

Good to know:
- the dataset contains a duplicate event where the data is loaded on a different day which we don't handle now and it is part of the first run, so it will not cause issues (we are taking the first loaded event)
- there is one row that is filtered because it happened earlier than the start_tstamp
