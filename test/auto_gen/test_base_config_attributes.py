from snowplow_signals.batch_autogen.models.modeling_step import (
    FilterCondition,
    ModelingCriteria,
    ModelingStep,
)

# Attribute templates for different test cases
first_value_attr = [
    ModelingStep(
        step_type="filtered_events",
        enabled=False,
        aggregation=None,
        column_name="mkt_source",
        modeling_criteria=None,
    ),
    ModelingStep(
        step_type="daily_aggregation",
        enabled=True,
        aggregation="first",
        column_name="first_mkt_source",
        modeling_criteria=None,
    ),
    ModelingStep(
        step_type="attribute_aggregation",
        enabled=True,
        aggregation="first",
        column_name="first_mkt_source",
        modeling_criteria=None,
    ),
]

last_value_attr = [
    ModelingStep(
        step_type="filtered_events",
        enabled=False,
        aggregation=None,
        column_name="mkt_source",
        modeling_criteria=None,
    ),
    ModelingStep(
        step_type="daily_aggregation",
        enabled=True,
        aggregation="last",
        column_name="last_mkt_source",
        modeling_criteria=None,
    ),
    ModelingStep(
        step_type="attribute_aggregation",
        enabled=True,
        aggregation="last",
        column_name="last_mkt_source",
        modeling_criteria=None,
    ),
]

last_n_day_aggregates_attr = [
    ModelingStep(
        step_type="filtered_events",
        enabled=False,
        aggregation=None,
        column_name="revenue",
        modeling_criteria=None,
    ),
    ModelingStep(
        step_type="daily_aggregation",
        enabled=True,
        aggregation="sum",
        column_name="revenue",
        modeling_criteria=ModelingCriteria(
            all=[FilterCondition(operator=">", property="period", value=7)],
            any=[],
        ),
    ),
    ModelingStep(
        step_type="attribute_aggregation",
        enabled=True,
        aggregation="sum",
        column_name="revenue",
        modeling_criteria=ModelingCriteria(
            all=[FilterCondition(operator=">", property="period", value=7)],
            any=[],
        ),
    ),
]

unique_list_attr = [
    ModelingStep(
        step_type="filtered_events",
        enabled=False,
        aggregation=None,
        column_name="mkt_source",
        modeling_criteria=None,
    ),
    ModelingStep(
        step_type="daily_aggregation",
        enabled=True,
        aggregation="unique_list",
        column_name="unique_list_source",
        modeling_criteria=ModelingCriteria(
            all=[FilterCondition(operator=">", property="period", value=7)],
            any=[],
        ),
    ),
    ModelingStep(
        step_type="attribute_aggregation",
        enabled=True,
        aggregation="unique_list",
        column_name="unique_list_source",
        modeling_criteria=ModelingCriteria(
            all=[FilterCondition(operator=">", property="period", value=7)],
            any=[],
        ),
    ),
]

lifetime_aggregates_attr = [
    ModelingStep(
        step_type="filtered_events",
        enabled=False,
        aggregation=None,
        column_name="mkt_source",
        modeling_criteria=None,
    ),
    ModelingStep(
        step_type="daily_aggregation",
        enabled=True,
        aggregation="count",
        column_name="lifetime_count_source",
        modeling_criteria=None,
    ),
    ModelingStep(
        step_type="attribute_aggregation",
        enabled=True,
        aggregation="sum",
        column_name="lifetime_count_source",
        modeling_criteria=None,
    ),
]
