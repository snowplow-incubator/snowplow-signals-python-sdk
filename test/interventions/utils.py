from snowplow_signals import (
    AttributeKeyIdentifiers,
    InterventionCriterion,
    InterventionInstance,
    LinkAttributeKey,
    RuleIntervention,
)

example_intervention = {
    "name": "cycle_cart_count",
    "version": 1,
    "target_agents": None,
    "script_uri": None,
    "description": "Resets the number of add_to_cart events when it becomes more than three.",
    "owner": "peter@snowplowanalytics.com",
    "criteria": {
        "attribute": "sample_ecommerce_stream_features:add_to_cart_events_count",
        "operator": ">",
        "value": 3,
    },
    "target_attribute_keys": [{"name": "domain_sessionid"}],
}

another_intervention = {
    "name": "another_cycle_cart_count",
    "version": 2,
    "target_agents": None,
    "script_uri": None,
    "description": "Resets the number of add_to_cart events when it becomes more than three.",
    "owner": "peter@snowplowanalytics.com",
    "criteria": {
        "attribute": "sample_ecommerce_stream_features:add_to_cart_events_count",
        "operator": ">",
        "value": 3,
    },
    "target_attribute_keys": [{"name": "domain_sessionid"}],
}


def get_intervention_response() -> dict:
    return example_intervention


def get_interventions_response() -> list[dict]:
    return [example_intervention, another_intervention]


def get_example_intervention() -> RuleIntervention:
    return RuleIntervention(
        name=example_intervention["name"],
        version=example_intervention["version"],
        description=example_intervention["description"],
        owner=example_intervention["owner"],
        criteria=InterventionCriterion(
            attribute=example_intervention["criteria"]["attribute"],
            operator=example_intervention["criteria"]["operator"],
            value=example_intervention["criteria"]["value"],
        ),
        target_attribute_keys=[
            LinkAttributeKey(name=e["name"])
            for e in example_intervention["target_attribute_keys"]
        ],
    )


def get_publishable_intervention() -> (
    tuple[AttributeKeyIdentifiers, InterventionInstance]
):
    return AttributeKeyIdentifiers({"domain_userid": ["123"]}), InterventionInstance(
        name="test_intervention", version=1
    )


def get_intervention_stream() -> tuple[AttributeKeyIdentifiers, bytes]:
    import json
    import uuid

    instance = dict(
        intervention_id=str(uuid.uuid4()),
        name="test",
        version=1,
        target_attribute_key=dict(name="domain_userid", id="123"),
        attributes={},
    )

    return AttributeKeyIdentifiers(
        {"domain_userid": ["123"]}
    ), f"data: {json.dumps(instance, indent=None)}\n\n".encode("utf8")
