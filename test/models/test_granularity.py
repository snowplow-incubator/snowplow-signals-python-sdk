import pytest
from pydantic import ValidationError

from snowplow_signals import AtomicProperty, EntityProperty, EventProperty
from snowplow_signals.models import Attribute, Event, StreamAttributeGroup
from snowplow_signals.models.attribute_key import AttributeKey


class TestAtomicPropertyGranularity:
    """Test granularity field on AtomicProperty."""

    def test_granularity_defaults_to_none(self):
        prop = AtomicProperty(name="derived_tstamp")
        assert prop.granularity is None

    @pytest.mark.parametrize(
        "granularity", ["second", "minute", "hour", "day", "month", "year"]
    )
    def test_valid_granularity_accepted(self, granularity: str):
        prop = AtomicProperty(name="derived_tstamp", granularity=granularity)
        assert prop.granularity == granularity

    def test_week_granularity_rejected(self):
        with pytest.raises(ValidationError):
            AtomicProperty(name="derived_tstamp", granularity="week")

    def test_invalid_granularity_rejected(self):
        with pytest.raises(ValidationError):
            AtomicProperty(name="derived_tstamp", granularity="fortnight")

    @pytest.mark.parametrize(
        "ts_field",
        [
            "etl_tstamp",
            "collector_tstamp",
            "dvce_created_tstamp",
            "dvce_sent_tstamp",
            "refr_device_tstamp",
            "derived_tstamp",
            "true_tstamp",
        ],
    )
    def test_granularity_accepted_on_timestamp_fields(self, ts_field: str):
        prop = AtomicProperty(name=ts_field, granularity="day")
        assert prop.granularity == "day"

    def test_granularity_serialises_to_dict(self):
        prop = AtomicProperty(name="derived_tstamp", granularity="hour")
        d = prop.model_dump()
        assert d["granularity"] == "hour"

    def test_granularity_none_omitted_in_serialisation(self):
        prop = AtomicProperty(name="derived_tstamp")
        d = prop.model_dump(exclude_none=True)
        assert "granularity" not in d


class TestEventPropertyGranularity:
    """Test granularity field on EventProperty."""

    def test_granularity_defaults_to_none(self):
        prop = EventProperty(
            vendor="com.example", name="my_event", major_version=1, path="$.ts"
        )
        assert prop.granularity is None

    @pytest.mark.parametrize(
        "granularity", ["second", "minute", "hour", "day", "month", "year"]
    )
    def test_valid_granularity_accepted(self, granularity: str):
        prop = EventProperty(
            vendor="com.example",
            name="my_event",
            major_version=1,
            path="$.ts",
            granularity=granularity,
        )
        assert prop.granularity == granularity

    def test_week_granularity_rejected(self):
        with pytest.raises(ValidationError):
            EventProperty(
                vendor="com.example",
                name="my_event",
                major_version=1,
                path="$.ts",
                granularity="week",
            )

    def test_granularity_serialises_to_dict(self):
        prop = EventProperty(
            vendor="com.example",
            name="my_event",
            major_version=1,
            path="$.ts",
            granularity="day",
        )
        assert prop.model_dump()["granularity"] == "day"


class TestEntityPropertyGranularity:
    """Test granularity field on EntityProperty."""

    def test_granularity_defaults_to_none(self):
        prop = EntityProperty(
            vendor="com.example", name="user_ctx", major_version=1, path="$.ts"
        )
        assert prop.granularity is None

    @pytest.mark.parametrize(
        "granularity", ["second", "minute", "hour", "day", "month", "year"]
    )
    def test_valid_granularity_accepted(self, granularity: str):
        prop = EntityProperty(
            vendor="com.example",
            name="user_ctx",
            major_version=1,
            path="$.ts",
            granularity=granularity,
        )
        assert prop.granularity == granularity

    def test_week_granularity_rejected(self):
        with pytest.raises(ValidationError):
            EntityProperty(
                vendor="com.example",
                name="user_ctx",
                major_version=1,
                path="$.ts",
                granularity="week",
            )

    def test_granularity_serialises_to_dict(self):
        prop = EntityProperty(
            vendor="com.example",
            name="user_ctx",
            major_version=1,
            path="$.ts",
            granularity="month",
        )
        assert prop.model_dump()["granularity"] == "month"


class TestGranularityInAttributeGroup:
    """Test that granularity travels correctly through AttributeInput."""

    def test_active_days_30d_example(self):
        """Canonical active-days example from the RFC."""
        from datetime import timedelta

        group = StreamAttributeGroup(
            name="engagement",
            attribute_key=AttributeKey(name="domain_userid"),
            owner="test@example.com",
            attributes=[
                Attribute(
                    name="active_days_30d",
                    type="int32",
                    aggregation="approx_count_distinct",
                    property=AtomicProperty(
                        name="derived_tstamp", granularity="day"
                    ),
                    events=[Event(name="page_view")],
                    period=timedelta(days=30),
                )
            ],
        )
        attr = group.attributes[0]
        assert attr.property.granularity == "day"
        assert attr.aggregation == "approx_count_distinct"

    def test_hour_of_day_seasonality_example(self):
        """Example showing hour-of-day seasonality attribute."""
        group = StreamAttributeGroup(
            name="seasonality",
            attribute_key=AttributeKey(name="domain_userid"),
            owner="test@example.com",
            attributes=[
                Attribute(
                    name="last_active_hour",
                    type="unix_timestamp",
                    aggregation="last",
                    property=AtomicProperty(
                        name="collector_tstamp", granularity="hour"
                    ),
                    events=[Event(name="page_view")],
                )
            ],
        )
        assert group.attributes[0].property.granularity == "hour"
