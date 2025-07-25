from snowplow_signals.models.property_wrappers.entity import EntityProperty


class TestEntityProperty:
    """Test the EntityProperty class."""

    def test_entity_property_creation(self):
        entity_prop = EntityProperty(
            vendor="com.snowplowanalytics.snowplow.ecommerce",
            name="cart",
            major_version=1,
            path="total_value",
        )

        assert entity_prop.vendor == "com.snowplowanalytics.snowplow.ecommerce"
        assert entity_prop.name == "cart"
        assert entity_prop.major_version == 1

        expected = (
            "contexts_com_snowplowanalytics_snowplow_ecommerce_cart_1[0].total_value"
        )
        assert entity_prop._to_api_property() == expected

        entity_prop_with_index = EntityProperty(
            vendor="com.test",
            name="session_context",
            major_version=1,
            index=3,
            path="session_id",
        )

        expected_with_index = "contexts_com_test_session_context_1[3].session_id"
        assert entity_prop_with_index._to_api_property() == expected_with_index

    def test_entity_property_to_api_property_no_path(self):
        entity_prop = EntityProperty(
            vendor="com.example",
            name="UserContext",
            major_version=2,
            index=1,
            path="prop",
        )

        expected = "contexts_com_example_user_context_2[1].prop"
        assert entity_prop._to_api_property() == expected
