from snowplow_signals.models.property_wrappers.event import EventProperty


class TestEventProperty:
    """Test the EventProperty class."""

    def test_event_property_creation(self):
        """Test creating an EventProperty with valid parameters."""
        event_prop = EventProperty(
            vendor="com.snowplowanalytics.snowplow.ecommerce",
            name="snowplow_ecommerce_action",
            major_version=1,
            path="type",
        )

        assert event_prop.vendor == "com.snowplowanalytics.snowplow.ecommerce"
        assert event_prop.name == "snowplow_ecommerce_action"
        assert event_prop.major_version == 1

        expected = "unstruct_event_com_snowplowanalytics_snowplow_ecommerce_snowplow_ecommerce_action_1:type"
        assert event_prop._to_api_property() == expected

        event_prop_v2 = EventProperty(
            vendor="com.example", name="TestEvent", major_version=2, path="prop"
        )

        expected_v2 = "unstruct_event_com_example_test_event_2:prop"
        assert event_prop_v2._to_api_property() == expected_v2
