from datetime import timedelta

import pytest

from snowplow_signals import (
    Attribute,
    AttributeGroup,
    Criteria,
    Criterion,
    Event,
    PredictiveAttribute,
    attribute_reference,
    domain_sessionid,
)
from snowplow_signals.models import (
    AtomicProperty,
    AttributeGroupResponse,
    SourceGroupReference,
)


@pytest.fixture
def session_group() -> AttributeGroup:
    return AttributeGroup(
        name="session_stats",
        version=3,
        attribute_key=domain_sessionid,
        owner="test@example.com",
        attributes=[
            Attribute(
                name="page_views",
                type="int32",
                events=[Event(name="page_view")],
                aggregation="counter",
                period=timedelta(hours=1),
            )
        ],
    )


@pytest.fixture
def goal_criteria() -> Criteria:
    return Criteria(
        all=[
            Criterion(
                property=AtomicProperty(name="event_name"),
                operator="=",
                value="transaction",
            )
        ]
    )


class TestPredictiveAttribute:
    def test_attribute_reference_builds_source_group_reference(
        self, session_group: AttributeGroup
    ):
        assert session_group.attribute_reference("page_views") == SourceGroupReference(
            name="session_stats", version=3, attribute_name="page_views"
        )

    def test_accepts_source_group_references(self, goal_criteria: Criteria):
        ref = SourceGroupReference(
            name="session_stats", version=1, attribute_name="page_views"
        )

        pa = PredictiveAttribute(
            name="purchase_propensity",
            owner="test@example.com",
            input_attributes=[ref],
            goal_criteria=goal_criteria,
        )

        assert pa.input_attributes == [ref]

    def test_attribute_reference_accepts_fetched_attribute_group(
        self, session_group: AttributeGroup
    ):
        fetched = AttributeGroupResponse.model_validate(
            {
                **session_group.model_dump(mode="json", exclude_none=True),
                "full_name": "session_stats_v3",
                "feast_name": "session_stats_v3",
                "stream_source_name": "stream",
                "attribute_key_or_name": "domain_sessionid",
                "attribute_group_or_attribute_key_ttl": None,
                "attribute_key": {
                    "name": "domain_sessionid",
                    "blobl_path": "domain_sessionid",
                },
            }
        )

        assert attribute_reference(fetched, "page_views") == SourceGroupReference(
            name="session_stats", version=3, attribute_name="page_views"
        )

    def test_attribute_reference_rejects_unknown_attribute(
        self, session_group: AttributeGroup
    ):
        with pytest.raises(ValueError, match="not_an_attribute"):
            session_group.attribute_reference("not_an_attribute")

    def test_attribute_reference_rejects_offline_group(
        self, session_group: AttributeGroup
    ):
        batch_group = session_group.model_copy(update={"offline": True})

        with pytest.raises(ValueError, match="stream"):
            batch_group.attribute_reference("page_views")

    def test_requires_owner_email(
        self, session_group: AttributeGroup, goal_criteria: Criteria
    ):
        with pytest.raises(ValueError, match="owner"):
            PredictiveAttribute(
                name="purchase_propensity",
                owner="not-an-email",
                input_attributes=[session_group.attribute_reference("page_views")],
                goal_criteria=goal_criteria,
            )

    def test_serializes_without_client_side_publish_flag(
        self, session_group: AttributeGroup, goal_criteria: Criteria
    ):
        pa = PredictiveAttribute(
            name="purchase_propensity",
            owner="test@example.com",
            input_attributes=[session_group.attribute_reference("page_views")],
            goal_criteria=goal_criteria,
            is_published=True,
        )

        payload = pa.model_dump(mode="json", exclude_none=True)

        assert "is_published" not in payload
        assert payload["input_attributes"] == [
            {"name": "session_stats", "version": 3, "attribute_name": "page_views"}
        ]

    def test_rejects_missing_version(
        self, session_group: AttributeGroup, goal_criteria: Criteria
    ):
        with pytest.raises(ValueError, match="version"):
            PredictiveAttribute(
                name="purchase_propensity",
                version=None,  # pyright: ignore[reportArgumentType]
                owner="test@example.com",
                input_attributes=[session_group.attribute_reference("page_views")],
                goal_criteria=goal_criteria,
            )

    def test_rejects_none_excluded_events(
        self, session_group: AttributeGroup, goal_criteria: Criteria
    ):
        with pytest.raises(ValueError, match="excluded_events"):
            PredictiveAttribute(
                name="purchase_propensity",
                owner="test@example.com",
                input_attributes=[session_group.attribute_reference("page_views")],
                goal_criteria=goal_criteria,
                excluded_events=None,  # pyright: ignore[reportArgumentType]
            )
