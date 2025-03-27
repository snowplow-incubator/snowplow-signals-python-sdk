import re
from typing import Any, Dict, FrozenSet, List, Set

from pydantic import BaseModel

from snowplow_signals.dbt.models.modeling_step import (
    FilterCondition,
    ModelingCriteria,
    ModelingStep,
)


class DbtConfigGenerator(BaseModel):
    base_config_data: Dict[str, Any]

    def get_events_dict(self):

        parsed_events = self.base_config_data["events"]
        event_dict_list = []
        for event in parsed_events:
            cleaned_event = event.removeprefix("iglu:")
            vendor, name, format_type, version = cleaned_event.split("/")

            event_dict_list.append(
                {
                    "event_vendor": vendor,
                    "event_name": name,
                    "event_format": format_type,
                    "event_version": version,
                }
            )

        return event_dict_list

    def get_attributes_by_type(self, attribute_type):
        """Returns a list of attributes base on type (e.g. first_value_attributes, last_value_attributes, last_n_day_aggregates, lifetime_aggregates)"""

        first_value_attributes = []
        last_value_attributes = []
        last_n_day_aggregates = []
        lifetime_aggregates = []

        for attribute in self.base_config_data.get("transformed_attributes", []):
            for step in attribute:
                period = None
                if step["step_type"] == "daily_aggregation":
                    daily_agg_column_name = step["column_name"]
                if step["step_type"] == "attribute_aggregation":

                    # get last n day filter period
                    if step.get("filter"):
                        conditions = step["filter"]["condition"]
                        for condition in conditions:
                            if condition["property"] == "period":
                                period = int(condition["value"])

                    if step["aggregation"] == "first":
                        first_value_attributes.append(
                            {
                                "daily_agg_column_name": daily_agg_column_name,
                                "column_name": step["column_name"],
                                "period": period if period else None,
                                "aggregation_type": step["aggregation"],
                            }
                        )
                    elif step["aggregation"] == "last":
                        last_value_attributes.append(
                            {
                                "daily_agg_column_name": daily_agg_column_name,
                                "column_name": step["column_name"],
                                "period": period if period else None,
                                "aggregation_type": step["aggregation"],
                            }
                        )
                    elif period is not None:
                        if step["aggregation"] == "unique_list":
                            last_n_day_aggregates.append(
                                {
                                    "daily_agg_column_name": daily_agg_column_name,
                                    "column_name": step["column_name"],
                                    "period": period if period else None,
                                    "aggregation_type": "array_agg",
                                }
                            )
                        else:
                            last_n_day_aggregates.append(
                                {
                                    "daily_agg_column_name": daily_agg_column_name,
                                    "column_name": step["column_name"],
                                    "period": period if period else None,
                                    "aggregation_type": step["aggregation"],
                                }
                            )
                    else:
                        if step["aggregation"] == "unique_list":
                            lifetime_aggregates.append(
                                {
                                    "daily_agg_column_name": daily_agg_column_name,
                                    "column_name": step["column_name"],
                                    "period": None,
                                    "aggregation_type": "array_agg",
                                }
                            )
                        else:
                            lifetime_aggregates.append(
                                {
                                    "daily_agg_column_name": daily_agg_column_name,
                                    "column_name": step["column_name"],
                                    "period": None,
                                    "aggregation_type": step["aggregation"],
                                }
                            )

        type_mapping = {
            "first_value_attributes": first_value_attributes,
            "last_value_attributes": last_value_attributes,
            "last_n_day_aggregates": last_n_day_aggregates,
            "lifetime_aggregates": lifetime_aggregates,
        }

        if attribute_type not in type_mapping:
            raise ValueError(f"Invalid type: {attribute_type}")

        selected_list = type_mapping[attribute_type]
        deduped_list = list({frozenset(d.items()): d for d in selected_list}.values())

        return deduped_list

    def _get_condition_sql(self, conditions, condition_type) -> str:
        condition_sql_list = []
        for condition in conditions:
            operator = condition["operator"]
            property_name = condition["property"]
            value = condition["value"]
            if operator == "=":
                condition_sql = f" {property_name} = '{value}'"
            elif operator == "!=":
                condition_sql = f" {property_name} != '{value}'"
            elif operator == "like":
                condition_sql = f" {property_name} LIKE '%{value}%'"
            elif operator == "in":
                condition_sql = f" {property_name} IN({value})"
            else:
                raise ValueError(f"Unsupported operator: {operator}")
            condition_sql_list.append(condition_sql)
        return f" {condition_type} ".join(condition_sql_list)

    def create_dbt_config(self) -> Dict[str, Any]:
        """
        Process dbt config in case there are changes and prepare properties for the jinja template.
        """

        aggregate_attributes = []
        first_value_attributes = []
        last_value_attributes = []

        attributes = self.base_config_data.get("transformed_attributes", [])
        for attribute in attributes:
            for step in attribute:
                if step["step_type"] == "daily_aggregation":
                    if step["aggregation"] in ["first", "last"]:
                        # For first/last values, we need to reference the column directly
                        ref_column_name = step["column_name"]
                        if ref_column_name.startswith("first_"):
                            ref_column_name = ref_column_name[6:]  # Remove 'first_' prefix
                        elif ref_column_name.startswith("last_"):
                            ref_column_name = ref_column_name[5:]  # Remove 'last_' prefix

                        attribute_dict = {
                            "step_type": step["step_type"],
                            "aggregation": step["aggregation"],
                            "column_name": step["column_name"],
                            "condition_clause": ref_column_name,  # Use the cleaned column name
                        }
                        if step["aggregation"] == "first":
                            first_value_attributes.append(attribute_dict)
                        else:
                            last_value_attributes.append(attribute_dict)
                    else:
                        # Handle aggregation attributes (count, sum, etc.)
                        modeling_criteria = step.get("modeling_criteria")
                        if modeling_criteria:
                            if "all" in modeling_criteria:
                                and_conditions = modeling_criteria.get("all", [])
                                and_sql_conditions = self._get_condition_sql(and_conditions, "and")
                            if "any" in modeling_criteria:
                                or_conditions = modeling_criteria.get("any", [])
                                or_sql_conditions = self._get_condition_sql(or_conditions, "or")
                            # If both "all" and "any" conditions are present, it means they have OR conditions and also a list of events to filter on using a logical AND, the safest is to wrap the OR conditions in brackets
                            if len(and_sql_conditions) > 0 and len(or_sql_conditions) > 0:
                                condition_statement = (
                                    f"{and_sql_conditions} and ({or_sql_conditions})"
                                )
                            elif len(and_sql_conditions) > 0:
                                condition_statement = and_sql_conditions
                            elif len(or_sql_conditions) > 0:
                                condition_statement = or_sql_conditions
                            else:
                                condition_statement = ""

                            if step["aggregation"] == "unique_list":
                                # Use a property name from the current context
                                property_name = step.get("property_name", "value")  # Default to "value" if not specified
                                condition_clause = f"distinct case when {condition_statement} then {property_name} else null end"
                                aggregate_attributes.append(
                                    {
                                        "step_type": step["step_type"],
                                        "aggregation": "array_agg",
                                        "column_name": step["column_name"],
                                        "condition_clause": condition_clause,
                                    }
                                )
                            else:
                                condition_clause = (
                                    f"case when {condition_statement} then 1 else 0 end"
                                )
                                aggregate_attributes.append(
                                    {
                                        "step_type": step["step_type"],
                                        "aggregation": step["aggregation"],
                                        "column_name": step["column_name"],
                                        "condition_clause": condition_clause,
                                    }
                                )
                        else:
                            # No filter, just count all events
                            aggregate_attributes.append(
                                {
                                    "step_type": step["step_type"],
                                    "aggregation": step["aggregation"],
                                    "column_name": step["column_name"],
                                    "condition_clause": "1",
                                }
                            )

        config = {
            "filtered_events": {
                "events": self.get_events_dict(),
                "properties": self.base_config_data["properties"],
            },
            "daily_agg": {
                "daily_aggregate_attributes": aggregate_attributes,
                "daily_first_value_attributes": first_value_attributes,
                "daily_last_value_attributes": last_value_attributes,
            },
            "attributes": {
                "lifetime_aggregates": self.get_attributes_by_type("lifetime_aggregates"),
                "last_n_day_aggregates": self.get_attributes_by_type("last_n_day_aggregates"),
                "first_value_attributes": self.get_attributes_by_type("first_value_attributes"),
                "last_value_attributes": self.get_attributes_by_type("last_value_attributes"),
            },
        }

        return config
