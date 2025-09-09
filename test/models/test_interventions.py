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
