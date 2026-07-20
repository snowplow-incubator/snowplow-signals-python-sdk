import json

import httpx
import pytest
from pydantic import ValidationError
from respx import MockRouter

from snowplow_signals.models import (
    Attribute,
    AttributeGroup,
    AttributeKey,
    BatchAttributeGroup,
    BatchSource,
    Event,
    ExternalBatchAttributeGroup,
    Field,
    StreamAttributeGroup,
)
from snowplow_signals.signals import Signals


def test_view_without_owner_raises_validation_error():
    """Test that a View without owner raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        # Create a View without owner
        AttributeGroup(
            name="test_view",
            attribute_key=AttributeKey(name="test_entity"),
        )
    assert "owner" in str(exc_info.value)


def test_view_with_owner_passes_validation():
    """Test that a View with owner passes validation."""
    view_with_owner = AttributeGroup(
        name="test_view",
        attribute_key=AttributeKey(name="test_entity"),
        owner="test@example.com",
    )
    assert view_with_owner.owner == "test@example.com"


def test_stream_view_passes_validation():
    """Test that a StreamView passes validation."""
    stream_view = StreamAttributeGroup(
        name="test_view",
        attribute_key=AttributeKey(name="test_entity"),
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
        StreamAttributeGroup(
            name="test_view",
            attribute_key=AttributeKey(name="test_entity"),
            owner="test@example.com",
        )


def test_batch_view_passes_validation():
    """Test that a BatchView passes validation."""
    batch_view = BatchAttributeGroup(
        name="test_view",
        attribute_key=AttributeKey(name="test_entity"),
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
        BatchAttributeGroup(
            name="test_view",
            attribute_key=AttributeKey(name="test_entity"),
            owner="test@example.com",
        )


def test_external_batch_view_passes_validation():
    """Test that a ExternalBatchView passes validation."""
    external_batch_view = ExternalBatchAttributeGroup(
        name="test_view",
        attribute_key=AttributeKey(name="test_entity"),
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
            timestamp_field="timestamp_field",
        ),
    )
    assert external_batch_view.offline


def test_external_batch_view_without_fields_raises_validation_error():
    """Test that a ExternalBatchView without fields raises ValidationError."""
    with pytest.raises(ValidationError):
        ExternalBatchAttributeGroup(
            name="test_view",
            attribute_key=AttributeKey(name="test_entity"),
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
        ExternalBatchAttributeGroup(
            name="test_view",
            attribute_key=AttributeKey(name="test_entity"),
            owner="test@example.com",
            fields=[
                Field(
                    name="id",
                    type="int32",
                )
            ],
        )


class TestAttributeGroupGetAttributes:
    """Test cases for attribute_group.get_attributes() API request structure."""

    def test_stream_attribute_group_get_attributes_api_request(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        """Test that StreamAttributeGroup.get_attributes() creates correct API request with all attributes."""

        stream_attribute_group = StreamAttributeGroup(
            name="user_metrics",
            version=1,
            attribute_key=AttributeKey(name="user_id"),
            owner="test@example.com",
            attributes=[
                Attribute(
                    name="page_views_count",
                    aggregation="counter",
                    type="int32",
                    events=[Event(name="page_view")],
                ),
                Attribute(
                    name="session_duration_avg",
                    aggregation="mean",
                    type="float",
                    events=[Event(name="session_end")],
                ),
            ],
        )

        def check_api_request(request):
            body = json.loads(request.content)

            assert body["attribute_keys"] == {"user_id": ["user-123"]}
            assert set(body["attributes"]) == {
                "user_metrics_v1:page_views_count",
                "user_metrics_v1:session_duration_avg",
            }

            return httpx.Response(
                200,
                json={
                    "user_id": ["user-123"],
                    "page_views_count": [42],
                    "session_duration_avg": [120.5],
                },
            )

        respx_mock.post("http://localhost:8000/api/v1/get-online-attributes").mock(
            side_effect=check_api_request
        )

        result = stream_attribute_group.get_attributes(signals_client, "user-123")
        assert result is not None

    def test_external_batch_attribute_group_get_attributes_api_request(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        """Test that ExternalBatchAttributeGroup.get_attributes() creates correct API request with all fields."""

        external_batch_attribute_group = ExternalBatchAttributeGroup(
            name="customer_profile",
            version=1,
            attribute_key=AttributeKey(name="customer_id"),
            owner="test@example.com",
            fields=[
                Field(name="first_name", type="string"),
                Field(name="last_name", type="string"),
                Field(name="email", type="string"),
                Field(name="registration_date", type="unix_timestamp"),
            ],
            batch_source=BatchSource(
                name="customer_table",
                database="warehouse",
                schema="public",
                table="customers",
                timestamp_field="updated_at",
            ),
        )

        def check_api_request(request):
            body = json.loads(request.content)

            assert body["attribute_keys"] == {"customer_id": ["cust-789"]}
            assert set(body["attributes"]) == {
                "customer_profile_v1:first_name",
                "customer_profile_v1:last_name",
                "customer_profile_v1:email",
                "customer_profile_v1:registration_date",
            }

            return httpx.Response(
                200,
                json={
                    "customer_id": ["cust-789"],
                    "first_name": ["John"],
                    "last_name": ["Doe"],
                },
            )

        respx_mock.post("http://localhost:8000/api/v1/get-online-attributes").mock(
            side_effect=check_api_request
        )

        result = external_batch_attribute_group.get_attributes(
            signals_client, "cust-789"
        )
        assert result is not None


def test_stream_view_with_most_frequent_aggregation():
    """Test that StreamAttributeGroup accepts most_frequent aggregation."""
    stream_view = StreamAttributeGroup(
        name="test_view",
        attribute_key=AttributeKey(name="test_entity"),
        owner="test@example.com",
        attributes=[
            Attribute(
                name="most_common_item",
                aggregation="most_frequent",
                type="string",
                events=[Event(name="purchase")],
            )
        ],
    )
    assert stream_view.attributes[0].aggregation == "most_frequent"


def test_stream_view_with_least_frequent_aggregation():
    """Test that StreamAttributeGroup accepts least_frequent aggregation."""
    stream_view = StreamAttributeGroup(
        name="test_view",
        attribute_key=AttributeKey(name="test_entity"),
        owner="test@example.com",
        attributes=[
            Attribute(
                name="least_common_item",
                aggregation="least_frequent",
                type="string",
                events=[Event(name="purchase")],
            )
        ],
    )
    assert stream_view.attributes[0].aggregation == "least_frequent"


def test_stream_view_with_category_count_aggregation():
    """Test that StreamAttributeGroup accepts category_count aggregation."""
    stream_view = StreamAttributeGroup(
        name="test_view",
        attribute_key=AttributeKey(name="test_entity"),
        owner="test@example.com",
        attributes=[
            Attribute(
                name="category_counts",
                aggregation="category_count",
                type="dict",
                events=[Event(name="purchase")],
            )
        ],
    )
    assert stream_view.attributes[0].aggregation == "category_count"
    assert stream_view.attributes[0].type == "dict"


def test_stream_view_with_approx_count_distinct_aggregation():
    """Test that StreamAttributeGroup accepts approx_count_distinct aggregation."""
    stream_view = StreamAttributeGroup(
        name="test_view",
        attribute_key=AttributeKey(name="test_entity"),
        owner="test@example.com",
        attributes=[
            Attribute(
                name="unique_visitors",
                aggregation="approx_count_distinct",
                type="int64",
                events=[Event(name="page_view")],
            )
        ],
    )
    assert stream_view.attributes[0].aggregation == "approx_count_distinct"


def test_attribute_granularity_day_on_unix_timestamp():
    """Test that granularity='day' is accepted on a unix_timestamp attribute."""
    stream_view = StreamAttributeGroup(
        name="test_view",
        attribute_key=AttributeKey(name="test_entity"),
        owner="test@example.com",
        attributes=[
            Attribute(
                name="active_days",
                aggregation="approx_count_distinct",
                type="unix_timestamp",
                events=[Event(name="page_view")],
                granularity="day",
            )
        ],
    )
    assert stream_view.attributes[0].granularity == "day"


def test_attribute_granularity_all_valid_values():
    """Test that all granularity values are accepted."""
    for granularity in ("second", "minute", "hour", "day", "week", "month", "year"):
        attr = Attribute(
            name="ts_attr",
            aggregation="approx_count_distinct",
            type="unix_timestamp",
            events=[Event(name="page_view")],
            granularity=granularity,
        )
        assert attr.granularity == granularity


def test_attribute_granularity_default_is_none():
    """Test that granularity defaults to None (backward-compatible)."""
    attr = Attribute(
        name="count_page_views",
        aggregation="counter",
        type="int32",
        events=[Event(name="page_view")],
    )
    assert attr.granularity is None


def test_attribute_granularity_on_unix_timestamp_list():
    """Test that granularity is accepted on unix_timestamp_list type."""
    attr = Attribute(
        name="session_timestamps",
        aggregation="approx_count_distinct",
        type="unix_timestamp_list",
        events=[Event(name="page_view")],
        granularity="week",
    )
    assert attr.granularity == "week"
