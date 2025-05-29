from snowplow_signals import (
    InterventionCriterion,
    InterventionSetAttributeContext,
    RuleIntervention,
)

example_intervention = {
    "name": "cycle_cart_count",
    "version": 1,
    "method": "set_attribute",
    "target_agents": None,
    "script_uri": None,
    "context": {
        "attribute": "sample_ecommerce_stream_features:add_to_cart_events_count",
        "value": 3,
        "clear_history": True,
    },
    "description": "Resets the number of add_to_cart events when it becomes more than three.",
    "tags": None,
    "owner": "peter@snowplowanalytics.com",
    "criteria": {
        "attribute": "sample_ecommerce_stream_features:add_to_cart_events_count",
        "operator": ">",
        "value": 3,
    },
}

another_intervention = {
    "name": "another_cycle_cart_count",
    "version": 2,
    "method": "set_attribute",
    "target_agents": None,
    "script_uri": None,
    "context": {
        "attribute": "sample_ecommerce_stream_features:add_to_cart_events_count",
        "value": 6,
        "clear_history": False,
    },
    "description": "Resets the number of add_to_cart events when it becomes more than three.",
    "tags": None,
    "owner": "peter@snowplowanalytics.com",
    "criteria": {
        "attribute": "sample_ecommerce_stream_features:add_to_cart_events_count",
        "operator": ">",
        "value": 3,
    },
}


def get_intervention_response() -> dict:
    return example_intervention


def get_interventions_response() -> list[dict]:
    return [example_intervention, another_intervention]


def get_example_intervention():
    return RuleIntervention(
        name=example_intervention["name"],
        version=example_intervention["version"],
        method=example_intervention["method"],
        context=InterventionSetAttributeContext(
            attribute=example_intervention["context"]["attribute"],
            value=example_intervention["context"]["value"],
            clear_history=example_intervention["context"]["clear_history"],
        ),
        description=example_intervention["description"],
        tags=example_intervention["tags"],
        owner=example_intervention["owner"],
        criteria=InterventionCriterion(
            attribute=example_intervention["criteria"]["attribute"],
            operator=example_intervention["criteria"]["operator"],
            value=example_intervention["criteria"]["value"],
        ),
    )
