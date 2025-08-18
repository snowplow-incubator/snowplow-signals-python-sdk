import re

import pytest

from snowplow_signals import AtomicProperty, EntityProperty, EventProperty
from snowplow_signals.models.criterion_wrapper import Criterion


class TestCriterionWrapper:
    """Test the Criterion wrapper class factory methods."""

    def test_eq_creates_correct_criterion(self):
        """Test that eq method creates a criterion with correct property, operator, and value."""
        atomic_prop = AtomicProperty(name="user_id")
        criterion = Criterion.eq(atomic_prop, "test_user")

        assert criterion.property == "user_id"
        assert criterion.operator == "="
        assert criterion.value == "test_user"

    def test_like_creates_correct_criterion(self):
        """Test that like method creates a criterion with correct operator for pattern matching."""
        atomic_prop = AtomicProperty(name="user_id")
        criterion = Criterion.like(atomic_prop, "%test%")

        assert criterion.property == "user_id"
        assert criterion.operator == "like"
        assert criterion.value == "%test%"

    def test_in_list_creates_correct_criterion(self):
        """Test that in_list method creates a criterion with 'in' operator and list value."""
        atomic_prop = AtomicProperty(name="platform")
        values = ["web", "mobile", "tablet"]
        criterion = Criterion.in_list(atomic_prop, values)

        assert criterion.property == "platform"
        assert criterion.operator == "in"
        assert criterion.value == ["web", "mobile", "tablet"]

    def test_eq_with_event_property(self):
        """Test that eq method works with EventProperty and generates correct property string."""
        event_prop = EventProperty(
            vendor="com.example", name="test_event", major_version=1, path="action"
        )
        criterion = Criterion.eq(event_prop, "click")

        assert criterion.property == "unstruct_event_com_example_test_event_1:action"
        assert criterion.operator == "="
        assert criterion.value == "click"

    def test_gte_with_entity_property(self):
        """Test that gte method works with EntityProperty and generates correct property string."""
        entity_prop = EntityProperty(
            vendor="com.example",
            name="user_context",
            major_version=1,
            path="age",
        )
        criterion = Criterion.gte(entity_prop, 18)

        assert criterion.property == "contexts_com_example_user_context_1[0].age"
        assert criterion.operator == ">="
        assert criterion.value == 18

    def test_negative_nested_index(self):
        """Test that negative indices for nested properties throw."""
        with pytest.raises(
            ValueError,
            match=re.escape("Negative indices are not supported: -1"),
        ):
            entity_prop = EntityProperty(
                vendor="com.example",
                name="user_context",
                major_version=1,
                path="array_attribute[-1].attr",
            )
            Criterion.gte(entity_prop, 18)
