import pytest
from pydantic import ValidationError

from snowplow_signals.models import View
from snowplow_signals.models.required_owner_view import RequiredOwnerView


def test_required_owner_view_requires_owner():
    """Test that RequiredOwnerView requires owner field."""
    # Should raise ValidationError when owner is not provided
    with pytest.raises(ValidationError) as exc_info:
        RequiredOwnerView(
            name="test_view",
            entity={"name": "test_entity"},
        )
    assert "owner" in str(exc_info.value)

    # Should work when owner is provided
    view = RequiredOwnerView(
        name="test_view",
        entity={"name": "test_entity"},
        owner="test@example.com",
    )
    assert view.owner == "test@example.com"


def test_required_owner_view_inherits_from_view():
    """Test that RequiredOwnerView inherits all View functionality."""
    # Create a View with all optional fields
    view_data = {
        "name": "test_view",
        "entity": {"name": "test_entity"},
        "owner": "test@example.com",
        "description": "Test description",
        "version": 2,
        "online": True,
        "offline": False,
        "tags": {"key": "value"},
    }

    # Both classes should accept the same data
    view = View(**view_data)
    required_owner_view = RequiredOwnerView(**view_data)

    # Verify all fields are inherited correctly
    for field in view_data:
        assert getattr(view, field) == getattr(required_owner_view, field)


def test_view_to_required_owner_view_conversion():
    """Test converting a View to RequiredOwnerView."""
    # Create a View with owner
    view = View(
        name="test_view",
        entity={"name": "test_entity"},
        owner="test@example.com",
    )

    # Convert to RequiredOwnerView
    required_owner_view = RequiredOwnerView.model_validate(view.model_dump())
    assert required_owner_view.owner == "test@example.com"

    # Create a View without owner
    view_no_owner = View(
        name="test_view",
        entity={"name": "test_entity"},
    )

    # Converting to RequiredOwnerView should raise ValidationError
    with pytest.raises(ValidationError) as exc_info:
        RequiredOwnerView.model_validate(view_no_owner.model_dump())
    assert "owner" in str(exc_info.value) 