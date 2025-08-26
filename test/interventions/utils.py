from snowplow_signals import (
    InterventionCriterion,
    RuleIntervention,
    LinkEntity,
)

example_intervention = {
    "name": "cycle_cart_count",
    "version": 1,
    "target_agents": None,
    "script_uri": None,
    "description": "Resets the number of add_to_cart events when it becomes more than three.",
    "tags": None,
    "owner": "peter@snowplowanalytics.com",
    "criteria": {
        "attribute": "sample_ecommerce_stream_features:add_to_cart_events_count",
        "operator": ">",
        "value": 3,
    },
    "target_entities": [{"name": "domain_sessionid"}],
}

another_intervention = {
    "name": "another_cycle_cart_count",
    "version": 2,
    "target_agents": None,
    "script_uri": None,
    "description": "Resets the number of add_to_cart events when it becomes more than three.",
    "tags": None,
    "owner": "peter@snowplowanalytics.com",
    "criteria": {
        "attribute": "sample_ecommerce_stream_features:add_to_cart_events_count",
        "operator": ">",
        "value": 3,
    },
    "target_entities": [{"name": "domain_sessionid"}],
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
        tags=example_intervention["tags"],
        owner=example_intervention["owner"],
        criteria=InterventionCriterion(
            attribute=example_intervention["criteria"]["attribute"],
            operator=example_intervention["criteria"]["operator"],
            value=example_intervention["criteria"]["value"],
        ),
        target_entities=[
            LinkEntity(name=e["name"]) for e in example_intervention["target_entities"]
        ],
    )
