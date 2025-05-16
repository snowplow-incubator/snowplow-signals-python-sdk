import pytest
from pydantic import ValidationError

from snowplow_signals.models import View


def test_view_without_owner_raises_validation_error():
    """Test that a View without owner raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        # Create a View without owner
        view_no_owner = View(
            name="test_view",
            entity={"name": "test_entity"},
        )
    assert "owner" in str(exc_info.value)


def test_view_with_owner_passes_validation():
    """Test that a View with owner passes validation."""
    view_with_owner = View(
        name="test_view",
        entity={"name": "test_entity"},
        owner="test@example.com",
    )
    assert view_with_owner.owner == "test@example.com"
