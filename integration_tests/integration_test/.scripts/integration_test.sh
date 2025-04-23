#!/bin/bash

# Expected input:
# -d (database) target database for dbt

while getopts 'd:' opt
do
  case $opt in
    d) DATABASE=$OPTARG
  esac
done

declare -a SUPPORTED_DATABASES=("snowflake")

# set to lower case
DATABASE="$(echo $DATABASE | tr '[:upper:]' '[:lower:]')"

if [[ $DATABASE == "all" ]]; then
  DATABASES=( "${SUPPORTED_DATABASES[@]}" )
else
  DATABASES=$DATABASE
fi

for db in ${DATABASES[@]}; do

  echo "Snowplow batch autogen integration tests: Seeding data"
  eval "dbt seed --full-refresh --target $db" || exit 1;

  echo "Snowplow batch autogen integration tests: Execute models - run 1/3"
  eval "dbt run --full-refresh --vars '{snowplow__allow_refresh: true}' --target $db" || exit 1;

  for i in {2..3}
  do
    echo "Snowplow batch autogen integration tests: Execute models - run $i/3"
    eval "dbt run --target $db" || exit 1;
  done

  echo "Snowplow batch autogen integration tests: Test models"

  eval "dbt test --store-failures --target $db" || exit 1;

  echo "Snowplow batch autogen integration tests: All tests passed"

done
