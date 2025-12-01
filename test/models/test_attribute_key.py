import pytest

from snowplow_signals import AttributeKey
from snowplow_signals.models import AtomicProperty, EntityProperty, EventProperty


class TestAttributeKey:
    def test_create_with_name_only(self):
        attr_key = AttributeKey(name="user_id")
        assert attr_key.name == "user_id"
        assert attr_key.key is None
        assert attr_key.property is None
        assert attr_key.external_column is None

    def test_create_with_deprecated_key_only_fails(self):
        with pytest.raises(ValueError, match="Name could not be derived from key only"):
            AttributeKey(key="session_id")

    def test_create_with_external_column(self):
        attr_key = AttributeKey(external_column="customer_id")
        assert attr_key.external_column == "customer_id"
        assert attr_key.name == "customer_id"

    def test_explicit_name_not_overridden_by_key(self):
        attr_key = AttributeKey(name="custom_name", key="session_id")
        assert attr_key.name == "custom_name"
        assert attr_key.key == "session_id"

    def test_name_derived_from_atomic_property(self):
        atomic_prop = AtomicProperty(name="user_id")
        attr_key = AttributeKey(property=atomic_prop)
        assert attr_key.name == "user_id"
        assert attr_key.property == atomic_prop

    def test_explicit_name_not_overridden_by_atomic_property(self):
        atomic_prop = AtomicProperty(name="user_id")
        attr_key = AttributeKey(name="custom_name", property=atomic_prop)

        assert attr_key.name == "custom_name"
        assert attr_key.property == atomic_prop

    def test_name_derived_from_event_property_simple_path(self):
        event_prop = EventProperty(
            vendor="com.example", name="test_event", major_version=1, path="$.user.id"
        )
        attr_key = AttributeKey(property=event_prop)

        assert attr_key.name == "id"
        assert attr_key.property == event_prop

    def test_name_derived_from_event_property_nested_path(self):
        event_prop = EventProperty(
            vendor="com.example",
            name="test_event",
            major_version=1,
            path="$.user.profile.email",
        )
        attr_key = AttributeKey(property=event_prop)

        assert attr_key.name == "email"

    def test_name_derived_from_event_property_with_array_access(self):
        event_prop = EventProperty(
            vendor="com.example",
            name="test_event",
            major_version=1,
            path="$.events[0].name",
        )
        attr_key = AttributeKey(property=event_prop)

        assert attr_key.name == "name"

    def test_explicit_name_not_overridden_by_event_property(self):
        event_prop = EventProperty(
            vendor="com.example", name="test_event", major_version=1, path="$.user.id"
        )
        attr_key = AttributeKey(name="custom_name", property=event_prop)

        assert attr_key.name == "custom_name"

    def test_name_derived_from_entity_property_simple_path(self):
        entity_prop = EntityProperty(
            vendor="com.example",
            name="user",
            major_version=1,
            path="$.profile.username",
        )
        attr_key = AttributeKey(property=entity_prop)

        assert attr_key.name == "username"
        assert attr_key.property == entity_prop

    def test_name_derived_from_entity_property_nested_path(self):
        entity_prop = EntityProperty(
            vendor="com.example",
            name="user",
            major_version=1,
            path="$.address.city.name",
        )
        attr_key = AttributeKey(property=entity_prop)

        assert attr_key.name == "name"

    def test_explicit_name_not_overridden_by_entity_property(self):
        entity_prop = EntityProperty(
            vendor="com.example",
            name="user",
            major_version=1,
            path="$.profile.username",
        )
        attr_key = AttributeKey(name="custom_name", property=entity_prop)

        assert attr_key.name == "custom_name"

    def test_external_column_takes_precedence_over_property(self):
        atomic_prop = AtomicProperty(name="user_id")
        attr_key = AttributeKey(external_column="customer_id", property=atomic_prop)

        assert attr_key.name == "customer_id"

    def test_name_and_external_column_must_match_when_both_provided(self):
        attr_key = AttributeKey(name="customer_id", external_column="customer_id")
        assert attr_key.name == "customer_id"
        assert attr_key.external_column == "customer_id"

        # Should fail when they don't match
        with pytest.raises(
            ValueError,
            match="If external_column is specified, it must be equal to the name of the AttributeKey",
        ):
            AttributeKey(name="user_id", external_column="customer_id")

    def test_create_without_any_fields_fails(self):
        """Test that creating AttributeKey without name or any derivable fields fails."""
        with pytest.raises(
            ValueError, match="Name should be provided if no other fields are set"
        ):
            AttributeKey()
