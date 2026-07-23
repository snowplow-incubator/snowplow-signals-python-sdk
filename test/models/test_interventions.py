import pytest
from pydantic import ValidationError

from snowplow_signals.models import (
    InterventionCriterion,
    LinkAttributeKey,
    RuleIntervention,
)


def test_view_without_owner_raises_validation_error():
    """Test that a View without owner raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        # Create a RuleIntervention without owner
        rule_intervention_no_owner = RuleIntervention(
            name="test_intervention",
            criteria=InterventionCriterion(
                attribute="sample_ecommerce_stream_features:add_to_cart_events_count",
                operator=">",
                value=3,
            ),
            target_attribute_keys=[LinkAttributeKey(name="domain_sessionid")],
        )
    assert "owner" in str(exc_info.value)


def test_view_with_owner_passes_validation():
    """Test that a View with owner passes validation."""
    view_with_owner = RuleIntervention(
        name="test_intervention",
        owner="test@example.com",
        criteria=InterventionCriterion(
            attribute="sample_ecommerce_stream_features:add_to_cart_events_count",
            operator=">",
            value=3,
        ),
        target_attribute_keys=[LinkAttributeKey(name="domain_sessionid")],
    )
    assert view_with_owner.owner == "test@example.com"


def test_changed_operator_criterion_without_value():
    """The 'changed' operator is accepted and needs no value."""
    criterion = InterventionCriterion(
        attribute="sample_ecommerce_stream_features:add_to_cart_events_count",
        operator="changed",
    )
    assert criterion.operator == "changed"
    assert criterion.value is None


def test_changed_operator_in_rule_intervention():
    """A RuleIntervention can use the 'changed' operator in its criteria."""
    intervention = RuleIntervention(
        name="test_intervention",
        owner="test@example.com",
        criteria=InterventionCriterion(
            attribute="sample_ecommerce_stream_features:add_to_cart_events_count",
            operator="changed",
        ),
        target_attribute_keys=[LinkAttributeKey(name="domain_sessionid")],
    )
    assert intervention.criteria.operator == "changed"


def test_invalid_operator_raises_validation_error():
    """An unknown operator is rejected by the criterion model."""
    with pytest.raises(ValidationError):
        InterventionCriterion(
            attribute="sample_ecommerce_stream_features:add_to_cart_events_count",
            operator="not_a_real_operator",
        )
