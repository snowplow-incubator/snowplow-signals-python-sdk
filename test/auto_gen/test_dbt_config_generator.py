from test.auto_gen.test_base_config_attributes import (
    first_value_attr,
    last_n_day_aggregates_attr,
    last_value_attr,
    lifetime_aggregates_attr,
    unique_list_attr,
)

import pytest

import snowplow_signals.batch_autogen.models.dbt_config_generator as dbg
from snowplow_signals.batch_autogen.models.base_config_generator import DbtBaseConfig
from snowplow_signals.batch_autogen.models.dbt_config_generator import (
    ConfigAttributes,
    ConfigEvents,
    DailyAggregations,
    DbtConfig,
    DbtConfigGenerator,
    FilteredEvents,
    FilteredEventsProperty,
)
from snowplow_signals.batch_autogen.models.modeling_step import (
    FilterCondition,
    ModelingStep,
)

"""Tests for the DbtConfigGenerator class"""


@pytest.fixture
def mock_base_config() -> DbtBaseConfig:
    mock_base_config = DbtBaseConfig(
        events=[
            "iglu:com.acme/Login/jsonschema/1-0-0",
            "iglu:io.foo/Buy/jsonschema/2-1-3",
        ],
        properties=[{"geo_country": "geo_country"}],
        periods=["P7DT0H0M0.000000S"],
        transformed_attributes=[],
        entity_key="domain_userid",
    )

    return mock_base_config


@pytest.fixture
def instance(mock_base_config) -> DbtConfigGenerator:
    obj = DbtConfigGenerator(base_config_data=mock_base_config, target_type="snowflake")
    obj.base_config_data = mock_base_config
    return obj


def test_get_events_dict_returns_expectation(instance: DbtConfigGenerator):
    result = instance.get_events_dict()

    assert isinstance(result, list)
    assert len(result) == 2

    assert result[0] == ConfigEvents(
        event_vendor="com.acme",
        event_name="Login",
        event_format="jsonschema",
        event_version="1-0-0",
    )

    assert result[1] == ConfigEvents(
        event_vendor="io.foo",
        event_name="Buy",
        event_format="jsonschema",
        event_version="2-1-3",
    )


def test_get_events_dict_with_missing_prefix(instance: DbtConfigGenerator):

    instance.base_config_data.events = ["com.vendor/event_name/jsonschema/1-0-0"]

    with pytest.raises(ValueError, match="does not start with 'iglu:'"):
        instance.get_events_dict()


def test_event_invalid_split(instance: DbtConfigGenerator):

    instance.base_config_data.events = ["iglu:com.vendor/event_name_only"]

    with pytest.raises(ValueError, match="does not have 4 parts separated by '/'"):
        instance.get_events_dict()


def test_first_value_attributes(instance: DbtConfigGenerator):
    instance.base_config_data.transformed_attributes = [first_value_attr]
    expectation = [
        {
            "daily_agg_column_name": "first_mkt_source",
            "column_name": "first_mkt_source",
            "period": None,
            "aggregation_type": "first",
        },
    ]
    result = instance.get_attributes_by_type("first_value_attributes")
    assert result == expectation


def test_last_value_attributes(instance: DbtConfigGenerator):
    instance.base_config_data.transformed_attributes = [last_value_attr]
    expectation = [
        {
            "daily_agg_column_name": "last_mkt_source",
            "column_name": "last_mkt_source",
            "period": None,
            "aggregation_type": "last",
        },
    ]
    result = instance.get_attributes_by_type("last_value_attributes")
    assert result == expectation


def test_lifetime_aggregate_attributes(instance: DbtConfigGenerator):
    instance.base_config_data.transformed_attributes = [lifetime_aggregates_attr]
    expectation = [
        {
            "daily_agg_column_name": "lifetime_count_source",
            "column_name": "lifetime_count_source",
            "period": None,
            "aggregation_type": "sum",
        },
    ]
    result = instance.get_attributes_by_type("lifetime_aggregates")
    assert result == expectation


def test_get_attributes_by_type_last_n_day_aggregates(instance: DbtConfigGenerator):
    instance.base_config_data.transformed_attributes = [last_n_day_aggregates_attr]

    result = instance.get_attributes_by_type("last_n_day_aggregates")

    # Expectation for last_n_day_aggregates with aggregation "unique_list" coerced to "array_agg"
    expectation = [
        {
            "daily_agg_column_name": "revenue",
            "column_name": "revenue",
            "period": 7,
            "aggregation_type": "sum",
        },
    ]
    assert result == expectation


def test_get_attributes_by_type_unique_list_attributes(instance: DbtConfigGenerator):
    instance.base_config_data.transformed_attributes = [unique_list_attr]

    result = instance.get_attributes_by_type("unique_list_attributes")

    # Expectation for "unique_list" aggregation coerced to "array_agg"
    expectation = [
        {
            "daily_agg_column_name": "unique_list_source",
            "column_name": "unique_list_source",
            "period": 7,
            "aggregation_type": "array_agg",
        },
    ]
    assert result == expectation


def test_get_attributes_by_type_duplicates(instance: DbtConfigGenerator):
    instance.base_config_data.transformed_attributes = [
        first_value_attr,
        first_value_attr,
    ]
    expectation = [
        {
            "daily_agg_column_name": "first_mkt_source",
            "column_name": "first_mkt_source",
            "period": None,
            "aggregation_type": "first",
        },
    ]
    result = instance.get_attributes_by_type("first_value_attributes")
    assert result == expectation


def test_get_attributes_by_type_invalid_type(instance: DbtConfigGenerator):
    instance.base_config_data.transformed_attributes = [first_value_attr]

    # Expect ValueError to be raised for invalid attribute_type
    with pytest.raises(ValueError, match="Invalid type: foobar"):
        instance.get_attributes_by_type("foobar")


def test_create_dbt_config_happy_path(instance: DbtConfigGenerator):
    instance.base_config_data.transformed_attributes = [
        first_value_attr,
        last_value_attr,
        last_n_day_aggregates_attr,
        lifetime_aggregates_attr,
        unique_list_attr,
    ]
    result = instance.create_dbt_config()

    expectation = DbtConfig(
        filtered_events=FilteredEvents(
            events=[
                ConfigEvents(
                    event_vendor="com.acme",
                    event_name="Login",
                    event_format="jsonschema",
                    event_version="1-0-0",
                ),
                ConfigEvents(
                    event_vendor="io.foo",
                    event_name="Buy",
                    event_format="jsonschema",
                    event_version="2-1-3",
                ),
            ],
            properties=[
                FilteredEventsProperty(
                    type="direct",
                    full_path="geo_country",
                    alias="geo_country",
                    column_prefix=None,
                )
            ],
        ),
        daily_agg=DailyAggregations(
            daily_aggregate_attributes=[
                {
                    "step_type": "daily_aggregation",
                    "aggregation": "sum",
                    "column_name": "revenue",
                    "condition_clause": "case when  period > 7 then cast(revenue as {{ dbt.type_float()}}) else 0 end",
                },
                {
                    "step_type": "daily_aggregation",
                    "aggregation": "count",
                    "column_name": "lifetime_count_source",
                    "condition_clause": "1",
                },
                {
                    "step_type": "daily_aggregation",
                    "aggregation": "array_agg",
                    "column_name": "unique_list_source",
                    "condition_clause": "distinct case when  period > 7 then mkt_source else null end",
                },
            ],
            daily_first_value_attributes=[
                {
                    "step_type": "daily_aggregation",
                    "aggregation": "first",
                    "column_name": "first_mkt_source",
                    "condition_clause": "mkt_source",
                }
            ],
            daily_last_value_attributes=[
                {
                    "step_type": "daily_aggregation",
                    "aggregation": "last",
                    "column_name": "last_mkt_source",
                    "condition_clause": "mkt_source",
                }
            ],
        ),
        attributes=ConfigAttributes(
            lifetime_aggregates=[
                {
                    "daily_agg_column_name": "lifetime_count_source",
                    "column_name": "lifetime_count_source",
                    "period": None,
                    "aggregation_type": "sum",
                }
            ],
            last_n_day_aggregates=[
                {
                    "daily_agg_column_name": "revenue",
                    "column_name": "revenue",
                    "period": 7,
                    "aggregation_type": "sum",
                }
            ],
            first_value_attributes=[
                {
                    "daily_agg_column_name": "first_mkt_source",
                    "column_name": "first_mkt_source",
                    "period": None,
                    "aggregation_type": "first",
                }
            ],
            last_value_attributes=[
                {
                    "daily_agg_column_name": "last_mkt_source",
                    "column_name": "last_mkt_source",
                    "period": None,
                    "aggregation_type": "last",
                }
            ],
            unique_list_attributes=[
                {
                    "daily_agg_column_name": "unique_list_source",
                    "column_name": "unique_list_source",
                    "period": 7,
                    "aggregation_type": "array_agg",
                }
            ],
        ),
    )
    assert result == expectation


def test_create_dbt_config_missing_column_name(instance: DbtConfigGenerator):

    first_value_attr_with_missing_column_name = [
        ModelingStep(
            step_type="filtered_events",
            enabled=False,
            aggregation=None,
            column_name="mkt_source",
            modeling_criteria=None,
        ),
        ModelingStep(
            step_type="daily_aggregation",
            enabled=True,
            aggregation="first",
            column_name="",
            modeling_criteria=None,
        ),
        ModelingStep(
            step_type="attribute_aggregation",
            enabled=True,
            aggregation="first",
            column_name="first_mkt_source",
            modeling_criteria=None,
        ),
    ]
    instance.base_config_data.transformed_attributes = [
        first_value_attr_with_missing_column_name
    ]

    with pytest.raises(
        ValueError, match="Column name is required for first/last value attributes"
    ):
        instance.create_dbt_config()


def test_get_property_references(instance):
    result = instance.get_property_references()
    assert result == [
        FilteredEventsProperty(
            type="direct",
            full_path="geo_country",
            alias="geo_country",
            column_prefix=None,
        )
    ]


def test_get_property_references_bigquery():
    instance = DbtConfigGenerator(
        base_config_data=mock_base_config, target_type="bigquery"
    )
    instance.base_config_data.properties = [{"geo_country": "geo_country"}]
    result = instance.get_property_references()
    assert result == [
        FilteredEventsProperty(
            type="direct",
            full_path="geo_country",
            alias="geo_country",
            column_prefix=None,
        )
    ]


def test_get_property_references_coalesced_bigquery():
    instance = DbtConfigGenerator(
        base_config_data=mock_base_config, target_type="bigquery"
    )
    instance.base_config_data.properties = [
        {
            "contexts_nl_basjes_yauaa_context_1[safe_offset(0)].operating_system_name": "operating_system_name"
        }
    ]
    result = instance.get_property_references()
    assert result == [
        FilteredEventsProperty(
            type="coalesced",
            full_path="contexts_nl_basjes_yauaa_context_1[safe_offset(0)].operating_system_name",
            alias="operating_system_name",
            column_prefix="contexts_nl_basjes_yauaa_context_1",
        )
    ]


def test_get_invalid_property_references_bigquery():
    instance = DbtConfigGenerator(
        base_config_data=mock_base_config, target_type="bigquery"
    )
    instance.base_config_data.properties = [{"foo": "foo"}]

    with pytest.raises(ValueError, match="Invalid property key: foo"):
        instance.get_property_references()
