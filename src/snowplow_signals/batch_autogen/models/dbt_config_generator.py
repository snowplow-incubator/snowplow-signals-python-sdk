from typing import Literal

from pydantic import BaseModel

from .dbt_project_setup import DbtBaseConfig
from .modeling_step import FilterCondition


class ConfigEvents(BaseModel):
    event_vendor: str
    event_name: str
    event_format: str
    event_version: str


class ConfigAttributes(BaseModel):
    lifetime_aggregates: list
    last_n_day_aggregates: list
    first_value_attributes: list
    last_value_attributes: list
    unique_list_attributes: list


class DailyAggregations(BaseModel):
    daily_aggregate_attributes: list
    daily_first_value_attributes: list
    daily_last_value_attributes: list


class FilteredEvents(BaseModel):
    events: list[ConfigEvents]
    properties: list[dict[str, str]]


class DbtConfig(BaseModel):
    filtered_events: FilteredEvents
    daily_agg: DailyAggregations
    attributes: ConfigAttributes


SQLConditions = Literal["and", "or"]


class DbtConfigGenerator:
    def __init__(self, base_config_data: DbtBaseConfig):
        self.base_config_data = base_config_data

    def get_events_dict(self) -> list[ConfigEvents]:
        parsed_events = self.base_config_data.events
        event_dict_list: list[ConfigEvents] = []
        for event in parsed_events:
            if not event.startswith("iglu:"):
                raise ValueError(f"Event '{event}' does not start with 'iglu:' prefix.")
            cleaned_event = event.removeprefix("iglu:")

            parts = cleaned_event.split("/")
            if len(parts) != 4:
                raise ValueError(
                    f"Event '{event}' does not have 4 parts separated by '/'."
                )

            vendor, name, format_type, version = parts

            event_dict_list.append(
                ConfigEvents(
                    event_vendor=vendor,
                    event_name=name,
                    event_format=format_type,
                    event_version=version,
                )
            )

        return event_dict_list

    def get_attributes_by_type(self, attribute_type) -> list:
        """Returns a list of attributes base on type that is needed to create jinja context for the attributes table (e.g. first_value_attributes, last_value_attributes, last_n_day_aggregates, lifetime_aggregates)"""

        first_value_attributes = []
        last_value_attributes = []
        last_n_day_aggregates = []
        lifetime_aggregates = []
        unique_list_attributes = []

        for attribute in self.base_config_data.transformed_attributes:
            for step in attribute:
                period = None
                if step.step_type == "daily_aggregation":
                    daily_agg_column_name = step.column_name
                if step.step_type == "attribute_aggregation":
                    # get last n day filter period
                    if step.modeling_criteria:
                        # Check "all" conditions first
                        if step.modeling_criteria.all:
                            for condition in step.modeling_criteria.all:
                                if condition.property == "period":
                                    if isinstance(condition.value, bool):
                                        raise ValueError(
                                            "Value should not be boolean when period is specified"
                                        )
                                    period = int(condition.value)
                        # Check "any" conditions if period not found in "all"
                        if period is None and step.modeling_criteria.any:
                            for condition in step.modeling_criteria.any:
                                if condition.property == "period":
                                    if isinstance(condition.value, bool):
                                        raise ValueError(
                                            "Value should not be boolean when period is specified"
                                        )
                                    period = int(condition.value)

                    if step.aggregation == "first":
                        first_value_attributes.append(
                            {
                                "daily_agg_column_name": daily_agg_column_name,
                                "column_name": step.column_name,
                                "period": period if period else None,
                                "aggregation_type": step.aggregation,
                            }
                        )
                    elif step.aggregation == "last":
                        last_value_attributes.append(
                            {
                                "daily_agg_column_name": daily_agg_column_name,
                                "column_name": step.column_name,
                                "period": period if period else None,
                                "aggregation_type": step.aggregation,
                            }
                        )
                    elif period is not None:
                        if step.aggregation == "unique_list":
                            unique_list_attributes.append(
                                {
                                    "daily_agg_column_name": daily_agg_column_name,
                                    "column_name": step.column_name,
                                    "period": period if period else None,
                                    "aggregation_type": "array_agg",
                                }
                            )
                        else:
                            last_n_day_aggregates.append(
                                {
                                    "daily_agg_column_name": daily_agg_column_name,
                                    "column_name": step.column_name,
                                    "period": period if period else None,
                                    "aggregation_type": step.aggregation,
                                }
                            )
                    else:
                        if step.aggregation == "unique_list":
                            unique_list_attributes.append(
                                {
                                    "daily_agg_column_name": daily_agg_column_name,
                                    "column_name": step.column_name,
                                    "period": None,
                                    "aggregation_type": "array_agg",
                                }
                            )
                        else:
                            lifetime_aggregates.append(
                                {
                                    "daily_agg_column_name": daily_agg_column_name,
                                    "column_name": step.column_name,
                                    "period": None,
                                    "aggregation_type": step.aggregation,
                                }
                            )

        type_mapping = {
            "first_value_attributes": first_value_attributes,
            "last_value_attributes": last_value_attributes,
            "last_n_day_aggregates": last_n_day_aggregates,
            "lifetime_aggregates": lifetime_aggregates,
            "unique_list_attributes": unique_list_attributes,
        }

        if attribute_type not in type_mapping:
            raise ValueError(f"Invalid type: {attribute_type}")

        selected_list = type_mapping[attribute_type]
        deduped_list = list({frozenset(d.items()): d for d in selected_list}.values())

        return deduped_list

    def _get_condition_sql(
        self, conditions: list[FilterCondition], condition_type: SQLConditions
    ) -> str:
        condition_sql_list = []
        for condition in conditions:
            operator = condition.operator
            property_name = condition.property
            value = condition.value
            if operator in ["<", ">", "<=", ">="] and isinstance(value, str):
                raise ValueError(
                    f"Cannot apply comparison operator '{operator}' on a string value: '{value}'."
                )
            if operator in ["=", "!=", "<", ">", "<=", ">="]:
                value_formatted = f"'{value}'" if isinstance(value, str) else value
                condition_sql = f" {property_name} {operator} {value_formatted}"
            elif operator == "like":
                condition_sql = f" {property_name} LIKE '%{value}%'"
            elif operator == "in":
                condition_sql = f" {property_name} IN({value})"
            else:
                raise ValueError(f"Unsupported operator: {operator}")
            if condition_sql == "":
                raise ValueError(f"Filter condition missing for condition: {condition}")
            condition_sql_list.append(condition_sql)
        return f" {condition_type} ".join(condition_sql_list)

    def get_daily_aggs_by_type(self, attribute_type) -> list:
        """Returns a list of attributes base on type that is needed to create jinja context for the daily_aggregates table (e.g. first_value_attributes, last_value_attributes, last_n_day_aggregates, lifetime_aggregates)"""

        aggregate_attributes = []
        first_value_attributes = []
        last_value_attributes = []

        attributes = self.base_config_data.transformed_attributes
        for attribute in attributes:
            for step in attribute:
                if step.step_type == "daily_aggregation":
                    if step.aggregation in ["first", "last"]:
                        # For first/last values, we need to reference the column directly

                        if step.column_name is None or step.column_name == "":
                            raise ValueError(
                                "Column name is required for first/last value attributes"
                            )
                        ref_column_name: str = step.column_name

                        if ref_column_name.startswith("first_"):
                            ref_column_name = ref_column_name[
                                6:
                            ]  # Remove 'first_' prefix
                        elif ref_column_name.startswith("last_"):
                            ref_column_name = ref_column_name[
                                5:
                            ]  # Remove 'last_' prefix

                        attribute_dict = {
                            "step_type": step.step_type,
                            "aggregation": step.aggregation,
                            "column_name": step.column_name,
                            "condition_clause": ref_column_name,  # Use the cleaned column name
                        }
                        if step.aggregation == "first":
                            first_value_attributes.append(attribute_dict)
                        else:
                            last_value_attributes.append(attribute_dict)
                    else:
                        # Handle aggregation attributes (count, sum, etc.)
                        modeling_criteria = step.modeling_criteria
                        if modeling_criteria:
                            and_sql_conditions = ""
                            or_sql_conditions = ""
                            if modeling_criteria.all:
                                and_conditions = modeling_criteria.all
                                and_sql_conditions = self._get_condition_sql(
                                    and_conditions, "and"
                                )
                            if modeling_criteria.any:
                                or_conditions = modeling_criteria.any
                                or_sql_conditions = self._get_condition_sql(
                                    or_conditions, "or"
                                )
                            # If both "all" and "any" conditions are present, it means they have OR conditions and also a list of events to filter on using a logical AND, the safest is to wrap the OR conditions in brackets
                            if (
                                len(and_sql_conditions) > 0
                                and len(or_sql_conditions) > 0
                            ):
                                condition_statement = (
                                    f"{and_sql_conditions} and ({or_sql_conditions})"
                                )
                            elif len(and_sql_conditions) > 0:
                                condition_statement = and_sql_conditions
                            elif len(or_sql_conditions) > 0:
                                condition_statement = or_sql_conditions
                            else:
                                condition_statement = ""

                            if step.aggregation == "unique_list":
                                property_name = attribute[0].column_name
                                condition_clause = f"distinct case when {condition_statement} then {property_name} else null end"
                                # FIXME we need to confirm this logic with a unit test
                                aggregate_attributes.append(
                                    {
                                        "step_type": step.step_type,
                                        "aggregation": "array_agg",
                                        "column_name": step.column_name,
                                        "condition_clause": condition_clause,
                                    }
                                )
                            else:
                                if step.aggregation == "count":
                                    condition_clause = f"case when {condition_statement} then 1 else 0 end"
                                elif step.aggregation == "sum":
                                    property_name = attribute[0].column_name
                                    condition_clause = f"case when {condition_statement} then cast({property_name} as {{{{ dbt.type_float()}}}}) else 0 end"
                                elif (
                                    step.aggregation == "min"
                                    or step.aggregation == "max"
                                ):
                                    property_name = attribute[0].column_name
                                    condition_clause = f"case when {condition_statement} then {property_name}) else null end"

                                aggregate_attributes.append(
                                    {
                                        "step_type": step.step_type,
                                        "aggregation": step.aggregation,
                                        "column_name": step.column_name,
                                        "condition_clause": condition_clause,
                                    }
                                )
                        else:
                            # No filter, just count all events
                            aggregate_attributes.append(
                                {
                                    "step_type": step.step_type,
                                    "aggregation": step.aggregation,
                                    "column_name": step.column_name,
                                    "condition_clause": "1",
                                }
                            )

        type_mapping = {
            "aggregate_attributes": aggregate_attributes,
            "first_value_attributes": first_value_attributes,
            "last_value_attributes": last_value_attributes,
        }

        if attribute_type not in type_mapping:
            raise ValueError(f"Invalid type: {attribute_type}")

        selected_list = type_mapping[attribute_type]
        deduped_list = list({frozenset(d.items()): d for d in selected_list}.values())

        return deduped_list

    def create_dbt_config(self) -> DbtConfig:
        """
        Process dbt config in case there are changes and prepare properties for the jinja template.
        """

        return DbtConfig(
            filtered_events=FilteredEvents(
                events=self.get_events_dict(),
                properties=self.base_config_data.properties,
            ),
            daily_agg=DailyAggregations(
                daily_aggregate_attributes=self.get_daily_aggs_by_type(
                    "aggregate_attributes"
                ),
                daily_first_value_attributes=self.get_daily_aggs_by_type(
                    "first_value_attributes"
                ),
                daily_last_value_attributes=self.get_daily_aggs_by_type(
                    "last_value_attributes"
                ),
            ),
            attributes=ConfigAttributes(
                lifetime_aggregates=self.get_attributes_by_type("lifetime_aggregates"),
                last_n_day_aggregates=self.get_attributes_by_type(
                    "last_n_day_aggregates"
                ),
                first_value_attributes=self.get_attributes_by_type(
                    "first_value_attributes"
                ),
                last_value_attributes=self.get_attributes_by_type(
                    "last_value_attributes"
                ),
                unique_list_attributes=self.get_attributes_by_type(
                    "unique_list_attributes"
                ),
            ),
        )
