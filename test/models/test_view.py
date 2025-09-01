import pytest
from pydantic import ValidationError

from snowplow_signals.models import (
    Attribute,
    AttributeKey,
    BatchSource,
    BatchView,
    Event,
    ExternalBatchView,
    Field,
    StreamView,
    View,
)


def test_view_without_owner_raises_validation_error():
    """Test that a View without owner raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        # Create a View without owner
        View(
            name="test_view",
            entity=AttributeKey(name="test_entity"),
        )
    assert "owner" in str(exc_info.value)


def test_view_with_owner_passes_validation():
    """Test that a View with owner passes validation."""
    view_with_owner = View(
        name="test_view",
        entity=AttributeKey(name="test_entity"),
        owner="test@example.com",
    )
    assert view_with_owner.owner == "test@example.com"


def test_stream_view_passes_validation():
    """Test that a StreamView passes validation."""
    stream_view = StreamView(
        name="test_view",
        entity=AttributeKey(name="test_entity"),
        owner="test@example.com",
        attributes=[
            Attribute(
                name="count_page_views",
                aggregation="counter",
                type="int32",
                events=[Event(name="page_view")],
            )
        ],
    )
    assert stream_view.owner == "test@example.com"
    assert stream_view.offline is False


def test_stream_view_without_attributes_raises_validation_error():
    """Test that a StreamView without attributes raises ValidationError."""
    with pytest.raises(ValidationError):
        StreamView(
            name="test_view",
            entity=AttributeKey(name="test_entity"),
            owner="test@example.com",
        )


def test_batch_view_passes_validation():
    """Test that a BatchView passes validation."""
    batch_view = BatchView(
        name="test_view",
        entity=AttributeKey(name="test_entity"),
        owner="test@example.com",
        attributes=[
            Attribute(
                name="count_page_views",
                aggregation="counter",
                type="int32",
                events=[Event(name="page_view")],
            )
        ],
    )
    assert batch_view.offline


def test_batch_view_without_attributes_raises_validation_error():
    """Test that a BatchView without attributes raises ValidationError."""
    with pytest.raises(ValidationError):
        BatchView(
            name="test_view",
            entity=AttributeKey(name="test_entity"),
            owner="test@example.com",
        )


def test_external_batch_view_passes_validation():
    """Test that a ExternalBatchView passes validation."""
    external_batch_view = ExternalBatchView(
        name="test_view",
        entity=AttributeKey(name="test_entity"),
        owner="test@example.com",
        fields=[
            Field(
                name="id",
                type="int32",
            )
        ],
        batch_source=BatchSource(
            name="test_batch_source",
            database="test_database",
            schema="test_schema",
            table="test_table",
        ),
    )
    assert external_batch_view.offline


def test_external_batch_view_without_fields_raises_validation_error():
    """Test that a ExternalBatchView without fields raises ValidationError."""
    with pytest.raises(ValidationError):
        ExternalBatchView(
            name="test_view",
            entity=AttributeKey(name="test_entity"),
            owner="test@example.com",
            fields=[],
            batch_source=BatchSource(
                name="test_batch_source",
                database="test_database",
                schema="test_schema",
                table="test_table",
            ),
        )


def test_external_batch_view_without_batch_source_raises_validation_error():
    """Test that a ExternalBatchView without batch_source raises ValidationError."""
    with pytest.raises(ValidationError):
        ExternalBatchView(
            name="test_view",
            entity=AttributeKey(name="test_entity"),
            owner="test@example.com",
            fields=[
                Field(
                    name="id",
                    type="int32",
                )
            ],
        )
