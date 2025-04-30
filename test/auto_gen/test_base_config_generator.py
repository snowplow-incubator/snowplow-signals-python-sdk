from datetime import timedelta

import pytest

from snowplow_signals.batch_autogen.models.base_config_generator import (
    BaseConfigGenerator,
)
from snowplow_signals.models import (
    AttributeOutput,
    BatchSource,
    Criteria,
    Criterion,
    Event,
    LinkEntity,
    ViewOutput,
)


@pytest.fixture
def test_view_output():
    return ViewOutput(
        name="test_view",
        version=1,
        entity=LinkEntity(name="user"),
        ttl=timedelta(days=30),
        batch_source=BatchSource(
            name="test_source",
            timestamp_field="event_time",
            created_timestamp_column="created_at",
            description="Test batch source",
            tags={"test": "value"},
            owner="test_owner",
            date_partition_column="date",
            database="test_db",
            schema="test_schema",
            table="test_table",
        ),
        online=True,
        description="Test view",
        tags={"test": "value"},
        owner="test_owner",
        fields=[],
        feast_name="test_feast",
        offline=True,
        stream_source_name="test_stream",
        attributes=[],
    )


@pytest.fixture
def base_config_generator(test_view_output):
    return BaseConfigGenerator(data=test_view_output)


class TestBaseConfigGenerator:
    def test_generate_column_name_basic(self, base_config_generator):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute",
            type="int32",
            tags={"test": "value"},
            events=[Event(vendor="com.test", name="test_event", version="1-0-0")],
            aggregation="counter",
            property=None,
            criteria=None,
            period=None,
        )
        result = base_config_generator._generate_column_name(attribute, "count")
        assert result == "count_test_event"

    def test_generate_column_name_with_property(self, base_config_generator):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with property",
            type="float",
            tags={"test": "value"},
            events=[Event(vendor="com.test", name="test_event", version="1-0-0")],
            aggregation="sum",
            property="contexts_com_test_context_1[0].test_property",
            criteria=None,
            period=None,
        )
        result = base_config_generator._generate_column_name(attribute, "sum")
        assert result == "sum_test_property_test_event"

    def test_generate_column_name_with_filter_conditions(self, base_config_generator):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with filter conditions",
            type="int32",
            tags={"test": "value"},
            events=[Event(vendor="com.test", name="test_event", version="1-0-0")],
            aggregation="counter",
            property=None,
            criteria=Criteria(
                all=[
                    Criterion(
                        property="contexts_com_test_context_1[0].test_property",
                        operator="=",
                        value="test_value",
                    )
                ],
                any=None,
            ),
            period=None,
        )
        result = base_config_generator._generate_column_name(attribute, "count")
        assert result == "count_test_event_test_property_eq_test_value"

    def test_generate_column_name_with_multiple_events(self, base_config_generator):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with multiple events",
            type="int32",
            tags={"test": "value"},
            events=[
                Event(vendor="com.test", name="test_event1", version="1-0-0"),
                Event(vendor="com.test", name="test_event2", version="1-0-0"),
            ],
            aggregation="counter",
            property=None,
            criteria=None,
            period=None,
        )
        result = base_config_generator._generate_column_name(attribute, "count")
        assert result == "count_test_event1_test_event2"

    def test_generate_column_name_with_special_characters(self, base_config_generator):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with special characters",
            type="int32",
            tags={"test": "value"},
            events=[Event(vendor="com.test", name="test-event", version="1-0-0")],
            aggregation="counter",
            property="contexts_com_test_context_1[0].test-property",
            criteria=None,
            period=None,
        )
        result = base_config_generator._generate_column_name(attribute, "count")
        assert result == "count_testproperty_testevent"

    def test_generate_column_name_with_numeric_start(self, base_config_generator):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with numeric start",
            type="int32",
            tags={"test": "value"},
            events=[Event(vendor="com.test", name="123test", version="1-0-0")],
            aggregation="counter",
            property=None,
            criteria=None,
            period=None,
        )
        result = base_config_generator._generate_column_name(attribute, "count")
        assert result == "count_123test"

    def test_generate_column_name_with_long_name(self, base_config_generator):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with long name",
            type="int32",
            tags={"test": "value"},
            events=[Event(vendor="com.test", name="a" * 100, version="1-0-0")],
            aggregation="counter",
            property=None,
            criteria=None,
            period=None,
        )
        result = base_config_generator._generate_column_name(attribute, "count")
        assert result == "test_attribute"  # Should return original name when too long

    def test_generate_column_name_with_empty_event_name(self, base_config_generator):
        # Create a valid attribute first
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with empty event name",
            type="int32",
            tags={"test": "value"},
            events=[Event(vendor="com.test", name="test_event", version="1-0-0")],
            aggregation="counter",
            property=None,
            criteria=None,
            period=None,
        )

        # Then modify the event name to be empty
        attribute.events[0].name = ""

        # Now test that it raises ValueError
        with pytest.raises(ValueError, match="Event name cannot be empty"):
            base_config_generator._generate_column_name(attribute, "count")

    def test_generate_modeling_steps_basic_counter(self, base_config_generator):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute",
            type="int32",
            tags={"test": "value"},
            events=[Event(vendor="com.test", name="test_event", version="1-0-0")],
            aggregation="counter",
            property=None,
            criteria=None,
            period=None,
        )
        steps = base_config_generator._generate_modeling_steps(attribute)

        assert len(steps) == 3
        assert steps[0].step_type == "filtered_events"
        assert steps[1].step_type == "daily_aggregation"
        assert steps[2].step_type == "attribute_aggregation"

        # Check daily aggregation step
        assert steps[1].aggregation == "count"
        assert steps[1].column_name == "count_test_event"
        assert steps[1].modeling_criteria.all[0].property == "event_name"
        assert steps[1].modeling_criteria.all[0].operator == "in"
        assert steps[1].modeling_criteria.all[0].value == "'test_event'"

        # Check final aggregation step
        assert steps[2].aggregation == "sum"  # count becomes sum in final aggregation
        assert steps[2].column_name == "test_attribute"

    def test_generate_modeling_steps_first_last_aggregation(
        self, base_config_generator
    ):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with first aggregation",
            type="int32",
            tags={"test": "value"},
            events=[Event(vendor="com.test", name="test_event", version="1-0-0")],
            aggregation="first",
            property="contexts_com_test_context_1[0].test_property",
            criteria=None,
            period=None,
        )
        steps = base_config_generator._generate_modeling_steps(attribute)

        assert len(steps) == 3
        assert steps[1].aggregation == "first"
        assert steps[1].column_name == "first_test_property"

    def test_generate_modeling_steps_with_filter_conditions(
        self, base_config_generator
    ):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with filter conditions",
            type="int32",
            tags={"test": "value"},
            events=[Event(vendor="com.test", name="test_event", version="1-0-0")],
            aggregation="counter",
            property=None,
            criteria=Criteria(
                all=[
                    Criterion(
                        property="contexts_com_test_context_1[0].test_property",
                        operator="=",
                        value="test_value",
                    )
                ],
                any=None,
            ),
            period=None,
        )
        steps = base_config_generator._generate_modeling_steps(attribute)

        assert len(steps) == 3
        assert (
            len(steps[1].modeling_criteria.all) == 2
        )  # event condition + filter condition
        assert steps[1].modeling_criteria.all[1].property == "test_property"
        assert steps[1].modeling_criteria.all[1].operator == "="
        assert steps[1].modeling_criteria.all[1].value == "test_value"

    def test_generate_modeling_steps_with_period(self, base_config_generator):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with period",
            type="int32",
            tags={"test": "value"},
            events=[Event(vendor="com.test", name="test_event", version="1-0-0")],
            aggregation="counter",
            property=None,
            criteria=None,
            period=timedelta(days=7),
        )
        steps = base_config_generator._generate_modeling_steps(attribute)

        assert len(steps) == 3
        assert steps[2].modeling_criteria.all[0].property == "period"
        assert steps[2].modeling_criteria.all[0].operator == ">"
        assert steps[2].modeling_criteria.all[0].value == 7

    def test_generate_modeling_steps_unsupported_aggregation(
        self, base_config_generator
    ):
        # Create a valid attribute first
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with unsupported aggregation",
            type="int32",
            tags={"test": "value"},
            events=[Event(vendor="com.test", name="test_event", version="1-0-0")],
            aggregation="counter",  # Start with valid aggregation
            property=None,
            criteria=None,
            period=None,
        )

        # Then modify the aggregation to be unsupported
        attribute.aggregation = "unsupported"  # type: ignore

        with pytest.raises(ValueError, match="Unsupported aggregation: unsupported"):
            base_config_generator._generate_modeling_steps(attribute)

    def test_generate_modeling_steps_first_last_without_property(
        self, base_config_generator
    ):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with first aggregation but no property",
            type="int32",
            tags={"test": "value"},
            events=[Event(vendor="com.test", name="test_event", version="1-0-0")],
            aggregation="first",
            property=None,  # Missing property for first aggregation
            criteria=None,
            period=None,
        )
        with pytest.raises(
            ValueError, match="Property cannot be None for first/last aggregation"
        ):
            base_config_generator._generate_modeling_steps(attribute)
