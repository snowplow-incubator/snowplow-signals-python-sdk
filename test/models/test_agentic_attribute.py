import pytest
from pydantic import ValidationError

from snowplow_signals import (
    AgenticAttribute,
    AgenticAttributeEvaluationPolicy,
    AgenticAttributeValue,
    CriteriaTrigger,
    EventLog,
    EventLogAtomicProperty,
    EventLogEvent,
    EventSelection,
    TriggerCriteriaAll,
    TriggerCriteriaAny,
    TriggerCriterion,
    domain_sessionid,
)
from snowplow_signals.models import LinkAttributeKey


def make_event_log() -> EventLog:
    return EventLog(
        name="recent_events",
        attribute_key=domain_sessionid,
        events=[
            EventSelection(
                event=EventLogEvent(
                    name="page_view",
                    vendor="com.snowplowanalytics.snowplow",
                    version="1-0-0",
                ),
                properties=[EventLogAtomicProperty(name="page_url")],
            )
        ],
        max_events=10,
        max_age_seconds=600,
    )


def make_trigger() -> CriteriaTrigger:
    return CriteriaTrigger(
        criteria=TriggerCriterion(
            attribute="session_stats:page_views",
            operator=">",
            value=3,
        )
    )


def test_accepts_attribute_key_and_event_log_objects():
    agentic_attribute = AgenticAttribute(
        name="shopper_intent",
        attribute_key=domain_sessionid,
        output_type="enum",
        values=[
            AgenticAttributeValue(name="browsing", description="Just looking."),
            AgenticAttributeValue(name="stuck", description="Can't find a product."),
        ],
        goal="Decide what the shopper is trying to do.",
        contexts=[make_event_log(), "other_events"],
        triggers=[make_trigger()],
    )

    assert agentic_attribute.attribute_key == LinkAttributeKey(name="domain_sessionid")
    assert agentic_attribute.contexts == ["recent_events", "other_events"]
    assert agentic_attribute.is_published is False

    dumped = agentic_attribute.model_dump(mode="json", exclude_none=True)
    assert dumped["attribute_key"] == {"name": "domain_sessionid"}
    assert dumped["contexts"] == ["recent_events", "other_events"]
    assert dumped["triggers"] == [
        {
            "type": "criteria",
            "criteria": {
                "attribute": "session_stats:page_views",
                "operator": ">",
                "value": 3,
            },
        }
    ]


def test_combines_trigger_criteria():
    trigger = CriteriaTrigger(
        criteria=TriggerCriteriaAll(
            all=[
                TriggerCriterion(
                    attribute="session_stats:page_views", operator=">", value=3
                ),
                TriggerCriteriaAny(
                    any=[
                        TriggerCriterion(
                            attribute="session_stats:searches", operator=">=", value=2
                        ),
                        TriggerCriterion(
                            attribute="session_stats:add_to_carts",
                            operator="=",
                            value=0,
                        ),
                    ]
                ),
            ]
        )
    )

    assert trigger.model_dump(mode="json", exclude_none=True) == {
        "type": "criteria",
        "criteria": {
            "all": [
                {"attribute": "session_stats:page_views", "operator": ">", "value": 3},
                {
                    "any": [
                        {
                            "attribute": "session_stats:searches",
                            "operator": ">=",
                            "value": 2,
                        },
                        {
                            "attribute": "session_stats:add_to_carts",
                            "operator": "=",
                            "value": 0,
                        },
                    ]
                },
            ]
        },
    }


def test_dumps_evaluation_policy():
    agentic_attribute = AgenticAttribute(
        name="needs_help",
        attribute_key=LinkAttributeKey(name="domain_sessionid"),
        output_type="boolean",
        goal="Does the shopper need help?",
        contexts=["recent_events"],
        triggers=[make_trigger()],
        evaluation_policy=AgenticAttributeEvaluationPolicy(
            cooldown_seconds=60, max_per_session=1
        ),
    )

    dumped = agentic_attribute.model_dump(mode="json", exclude_none=True)
    assert dumped["evaluation_policy"] == {"cooldown_seconds": 60, "max_per_session": 1}


def test_requires_a_context():
    with pytest.raises(ValidationError):
        AgenticAttribute(
            name="needs_help",
            attribute_key=domain_sessionid,
            output_type="boolean",
            goal="Does the shopper need help?",
            contexts=[],
            triggers=[make_trigger()],
        )


def test_rejects_unknown_output_type():
    with pytest.raises(ValidationError):
        AgenticAttribute(
            name="needs_help",
            attribute_key=domain_sessionid,
            output_type="text",  # type: ignore[arg-type]
            goal="Does the shopper need help?",
            contexts=["recent_events"],
            triggers=[make_trigger()],
        )
