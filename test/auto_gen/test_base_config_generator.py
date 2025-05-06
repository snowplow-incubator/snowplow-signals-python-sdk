from datetime import timedelta

import pytest
from pydantic import ValidationError

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
            owner="test_owner",
            date_partition_column="date",
            database="test_db",
            schema="test_schema",
            table="test_table",
        ),
        online=True,
        description="Test view",
        owner="test_owner",
        fields=[],
        feast_name="test_feast",
        offline=True,
        stream_source_name="test_stream",
        entity_key="user_id",
        attributes=[],
        view_or_entity_ttl=timedelta(days=30),
    )


@pytest.fixture
def base_config_generator(test_view_output):
    return BaseConfigGenerator(data=test_view_output)


class TestBaseConfigGenerator:

    # Test _generate_column_name for a simple field
    def test_generate_column_name_basic(self, base_config_generator):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute",
            type="int32",
            events=[Event(vendor="com.test", name="test_event", version="1-0-0")],
            aggregation="counter",
            property=None,
            criteria=None,
            period=None,
        )
        result = base_config_generator._generate_column_name(attribute, "count")
        assert result == "count_test_event"

    def test_generate_column_name_with_special_characters(self, base_config_generator):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with special characters",
            type="int32",
            events=[Event(vendor="com.test", name="test-event", version="1-0-0")],
            aggregation="counter",
            property="contexts_com_test_context_1[0].test-property",
            criteria=None,
            period=None,
        )
        result = base_config_generator._generate_column_name(attribute, "count")
        assert result == "count_test_property_test_event"

    def test_generate_column_name_with_numeric_start(self, base_config_generator):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with numeric start",
            type="int32",
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
            events=[Event(vendor="com.test", name="a" * 100, version="1-0-0")],
            aggregation="counter",
            property=None,
            criteria=None,
            period=None,
        )
        result = base_config_generator._generate_column_name(attribute, "count")
        assert result == "test_attribute"  # Should return original name when too long

    def test_generate_column_name_with_property(self, base_config_generator):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with property",
            type="float",
            events=[Event(vendor="com.test", name="test_event", version="1-0-0")],
            aggregation="sum",
            property="contexts_com_test_context_1[0].test_property",
            criteria=None,
            period=None,
        )
        result = base_config_generator._generate_column_name(attribute, "sum")
        assert result == "sum_test_property_test_event"

    def test_generate_column_name_with_single_criteria(self, base_config_generator):
        """Test generate_column_name with a single criteria"""
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with filter conditions",
            type="int32",
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

    #
    def test_generate_column_name_with_multiple_criteria(self, base_config_generator):
        """Test generate_column_name with multiple criteria"""
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute",
            type="int32",
            events=[Event(vendor="com.test", name="test_event", version="1-0-0")],
            aggregation="counter",
            property=None,
            criteria=Criteria(
                any=[
                    Criterion(property="bar", operator=">", value=1),
                    Criterion(property="baz", operator="=", value="x"),
                ],
                all=None,
            ),
            period=None,
        )
        result = base_config_generator._generate_column_name(attribute, "count")
        assert result == "count_test_event_bar_gt_1_any_baz_eq_x"

    def test_generate_column_name_with_multiple_events(self, base_config_generator):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with multiple events",
            type="int32",
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

    def test_generate_column_name_with_empty_event_name(self, base_config_generator):
        # Create a valid attribute first
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with empty event name",
            type="int32",
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

    #
    def test_generate_column_name_basic_click_event(self, base_config_generator):
        """Test generate_column_name with basic case"""
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute",
            type="int32",
            events=[Event(vendor="com.test", name="click", version="1-0-0")],
            aggregation="counter",
            property=None,
            criteria=None,
            period=None,
        )
        result = base_config_generator._generate_column_name(attribute, "count")
        assert result == "count_click"

    #
    def test_generate_column_name_with_property_and_multiple_events(
        self, base_config_generator
    ):
        """Test generate_column_name with property and multiple events"""
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute",
            type="int32",
            events=[
                Event(vendor="com.test", name="login", version="1-0-0"),
                Event(vendor="com.test", name="purchase", version="1-0-0"),
            ],
            aggregation="sum",
            property="ctx:Amount",
            criteria=None,
            period=None,
        )
        result = base_config_generator._generate_column_name(attribute, "sum")
        assert result == "sum_amount_login_purchase"

    #
    def test_generate_column_name_edge_cases(self, base_config_generator):
        """Test generate_column_name with edge cases"""
        # Empty string in event name - not allowed by Event model
        with pytest.raises(
            ValidationError, match="String should have at least 1 character"
        ):
            attribute = AttributeOutput(
                name="test_attribute",
                description="Test attribute",
                type="int32",
                events=[Event(vendor="com.test", name="", version="1-0-0")],
                aggregation="counter",
                property=None,
                criteria=None,
                period=None,
            )

        # Special characters in event name - only alphanumeric, hyphens, and underscores allowed
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute",
            type="int32",
            events=[Event(vendor="com.test", name="test-event_123", version="1-0-0")],
            aggregation="counter",
            property=None,
            criteria=None,
            period=None,
        )
        result = base_config_generator._generate_column_name(attribute, "count")
        assert result == "count_test_event_123"  # Implementation removes hyphens

        # Multiple properties
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute",
            type="int32",
            events=[Event(vendor="com.test", name="test_event", version="1-0-0")],
            aggregation="counter",
            property="prop1:prop2:prop3",
            criteria=None,
            period=None,
        )
        result = base_config_generator._generate_column_name(attribute, "count")
        assert (
            result == "count_prop2_test_event"
        )  # Implementation takes second part after first colon

    # Test get_agg_short_name for all the supported aggregations
    def test_get_agg_short_name_supported_aggregations(self, base_config_generator):
        """Test get_agg_short_name with supported aggregations"""
        test_cases = [
            ("counter", "count"),
            ("sum", "sum"),
            ("min", "min"),
            ("max", "max"),
            ("first", "first"),
            ("last", "last"),
            ("unique_list", "unique_list"),
        ]
        for agg, expected in test_cases:
            assert base_config_generator.get_agg_short_name(agg) == expected

    # Test get_agg_short_name for non supported aggregation and invalid input types
    def test_get_agg_short_name_unsupported_aggregation(self, base_config_generator):
        """Test get_agg_short_name with unsupported aggregation and invalid input types"""
        assert base_config_generator.get_agg_short_name("mean") is None
        assert base_config_generator.get_agg_short_name(None) is None
        assert base_config_generator.get_agg_short_name("") is None
        assert base_config_generator.get_agg_short_name(123) is None

    # Test get_cleaned_property_name for classic custom context
    def test_get_cleaned_property_name_with_colon(self, base_config_generator):
        """Test get_cleaned_property_name with colon separator"""
        assert (
            base_config_generator.get_cleaned_property_name("fieldA:deviceClassLast")
            == "device_class_last"
        )

    # FIXME https://snplow.atlassian.net/browse/AISP-352
    def test_get_cleaned_property_name_with_dot(self, base_config_generator):
        """Test get_cleaned_property_name with dot separator"""
        assert (
            base_config_generator.get_cleaned_property_name("path.to:FieldName")
            == "field_name"
        )

    # Test get_cleaned_property_name for simple column (e.g mkt_source )
    def test_get_cleaned_property_name_simple(self, base_config_generator):
        """Test get_cleaned_property_name with simple field name"""
        assert (
            base_config_generator.get_cleaned_property_name("just_a_field")
            == "just_a_field"
        )

    #
    def test_get_cleaned_property_name_invalid_input(self, base_config_generator):
        """Test get_cleaned_property_name with invalid input"""
        assert base_config_generator.get_cleaned_property_name(None) is None
        assert base_config_generator.get_cleaned_property_name(123) is None

    def test_get_cleaned_property_name_multiple_separators(self, base_config_generator):
        """Test get_cleaned_property_name with multiple separators"""
        # The implementation takes the last part after the last separator
        assert (
            base_config_generator.get_cleaned_property_name(
                "path.to:fieldA:deviceClassLast"
            )
            == "field_a"
        )
        assert (
            base_config_generator.get_cleaned_property_name(
                "path.to.fieldA.deviceClassLast"
            )
            == "device_class_last"
        )

    #
    def test_get_cleaned_property_name_with_brackets(self, base_config_generator):
        """Test get_cleaned_property_name with bracketed context"""
        assert (
            base_config_generator.get_cleaned_property_name(
                "contexts_com_test_context_1[0]:deviceClassLast"
            )
            == "device_class_last"
        )
        assert (
            base_config_generator.get_cleaned_property_name(
                "contexts_com_test_context_1[0].deviceClassLast"
            )
            == "device_class_last"
        )

    def test_get_cleaned_property_name_edge_cases(self, base_config_generator):
        """Test get_cleaned_property_name with edge cases"""
        # Empty string
        assert base_config_generator.get_cleaned_property_name("") == ""

        # Only separators
        assert base_config_generator.get_cleaned_property_name("::") == ""
        assert base_config_generator.get_cleaned_property_name("...") == ""
        assert (
            base_config_generator.get_cleaned_property_name(":.:") == "."
        )  # Implementation returns last part

        # Special characters
        assert (
            base_config_generator.get_cleaned_property_name("test@#$%^&*()")
            == "test@#$%^&*()"
        )
        assert (
            base_config_generator.get_cleaned_property_name("test:field@#$%^&*()")
            == "field@#$%^&*()"
        )

    def test_add_to_properties_empty_entries(self, base_config_generator):
        """Test add_to_properties with empty key or value"""
        base_config_generator.add_to_properties({"": "x"})
        base_config_generator.add_to_properties({None: "x"})
        assert base_config_generator.properties == []

    #
    def test_add_to_properties_duplicate_entries(self, base_config_generator):
        """Test add_to_properties with duplicate entries"""
        base_config_generator.add_to_properties({"a": "b"})
        base_config_generator.add_to_properties({"a": "b"})
        assert base_config_generator.properties == [{"a": "b"}]

    #
    def test_get_filter_condition_name_component_mixed_operators(
        self, base_config_generator
    ):
        """Test get_filter_condition_name_component with mixed operators and special characters"""
        filter_condition = Criterion(property="FooBar", operator="!=", value="A B.%/C")
        result = base_config_generator._get_filter_condition_name_component(
            filter_condition
        )
        assert (
            result == "FooBar_neq_a_b_pct_c"
        )  # Property name is not converted to snake_case

    def test_generate_modeling_steps_basic_counter(self, base_config_generator):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute",
            type="int32",
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

    def test_generate_modeling_steps_first_aggregation(
        self, base_config_generator
    ):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with first aggregation",
            type="int32",
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

    def test_generate_modeling_steps_first_without_property(
        self, base_config_generator
    ):
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute with first aggregation but no property",
            type="int32",
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

    #
    def test_generate_modeling_steps_first_aggregation(self, base_config_generator):
        """Test generate_modeling_steps with first aggregation"""
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute",
            type="int32",
            events=[Event(vendor="com.test", name="test_event", version="1-0-0")],
            aggregation="first",
            property="test_property",
            criteria=None,
            period=None,
        )
        steps = base_config_generator._generate_modeling_steps(attribute)
        assert len(steps) == 3
        assert steps[1].step_type == "daily_aggregation"
        assert steps[1].column_name == "first_test_property"
        assert steps[2].column_name == "test_attribute"

    #
    def test_generate_modeling_steps_last_aggregation(self, base_config_generator):
        """Test generate_modeling_steps with last aggregation"""
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute",
            type="int32",
            events=[Event(vendor="com.test", name="test_event", version="1-0-0")],
            aggregation="last",
            property="test_property",
            criteria=None,
            period=None,
        )
        steps = base_config_generator._generate_modeling_steps(attribute)
        assert len(steps) == 3
        assert steps[1].step_type == "daily_aggregation"
        assert steps[1].column_name == "last_test_property"
        assert steps[2].column_name == "test_attribute"


    #
    def test_generate_modeling_steps_unique_list(self, base_config_generator):
        """Test generate_modeling_steps with unique_list aggregation"""
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute",
            type="string",
            events=[Event(vendor="com.test", name="test_event", version="1-0-0")],
            aggregation="unique_list",
            property="test_property",
            criteria=None,
            period=None,
        )
        steps = base_config_generator._generate_modeling_steps(attribute)
        assert len(steps) == 3
        assert steps[1].step_type == "daily_aggregation"
        assert steps[1].aggregation == "unique_list"
        assert steps[2].aggregation == "unique_list"

    #
    def test_generate_modeling_steps_empty_events(self, base_config_generator):
        """Test generate_modeling_steps with empty events list"""
        # The implementation requires at least one event
        with pytest.raises(ValueError, match="List should have at least 1 item"):
            attribute = AttributeOutput(
                name="test_attribute",
                description="Test attribute",
                type="int32",
                events=[],  # This will fail validation
                aggregation="counter",
                property=None,
                criteria=None,
                period=None,
            )
            base_config_generator._generate_modeling_steps(attribute)

    def test_generate_modeling_steps_invalid_event_name(self, base_config_generator):
        """Test generate_modeling_steps with invalid event name"""
        attribute = AttributeOutput(
            name="test_attribute",
            description="Test attribute",
            type="int32",
            events=[Event(vendor="com.test", name=None, version="1-0-0")],
            aggregation="counter",
            property=None,
            criteria=None,
            period=None,
        )
        with pytest.raises(ValueError, match="Event name cannot be None"):
            base_config_generator._generate_modeling_steps(attribute)

    # FIXME do we want to support empty attributes? Should we raise an error?
    def test_create_base_config_empty_attributes(self, base_config_generator):
        """Test create_base_config with empty attributes"""
        base_config_generator.data.attributes = []
        config = base_config_generator.create_base_config()
        assert config.events == []
        assert config.properties == []
        assert config.periods == []
        assert config.transformed_attributes == []
        assert config.entity_key == base_config_generator.data.entity_key

    # 
    def test_create_base_config_multiple_attributes(self, base_config_generator):
        """Test create_base_config with multiple attributes"""
        base_config_generator.data.attributes = [
            AttributeOutput(
                name="first_attr",
                description="First attribute",
                type="int32",
                events=[Event(vendor="com.test", name="test_event", version="1-0-0")],
                aggregation="first",
                property="test_property",
                criteria=None,
                period=None,
            ),
            AttributeOutput(
                name="unique_attr",
                description="Unique list attribute",
                type="string",
                events=[Event(vendor="com.test", name="test_event", version="1-0-0")],
                aggregation="unique_list",
                property="test_property",
                criteria=None,
                period=timedelta(days=30),
            ),
        ]
        config = base_config_generator.create_base_config()
        assert len(config.events) == 1
        assert len(config.properties) == 1
        assert len(config.periods) == 1
        assert len(config.transformed_attributes) == 2
        assert config.entity_key == base_config_generator.data.entity_key
