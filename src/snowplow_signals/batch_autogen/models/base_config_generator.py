import re
from collections import OrderedDict
from typing import Dict, FrozenSet, Literal, Set

from pydantic import BaseModel

from snowplow_signals.batch_autogen.models.modeling_step import (
    FilterCondition,
    ModelingCriteria,
    ModelingStep,
)

from ...models import AttributeOutput, Criterion, Event, ViewResponse
from ..utils.utils import timedelta_isoformat

from sqlglot.dialects.snowflake import Snowflake


# FIXME can we extract from auto generated model attributes ?
AggregationLiteral = Literal[
    "counter", "sum", "min", "max", "mean", "first", "last", "unique_list"
]
SQLAggregationLiteral = Literal[
    "count", "sum", "min", "max", "avg", "first", "last", "unique_list"
]
reserwed_words_dict = Snowflake.Tokenizer.KEYWORDS
SQL_RESERVED_WORDS = sorted(reserwed_words_dict.keys())


class DbtBaseConfig(BaseModel):
    events: list[str]
    properties: list[dict[str, str]]
    periods: list[str]
    transformed_attributes: list[list[ModelingStep]]
    entity_key: str


class BaseConfigGenerator:
    events: list[str]
    properties: list[dict[str, str]]
    periods: Set[str]
    data: ViewResponse

    def __init__(
        self,
        data: ViewResponse,
    ):
        self.data = data
        self.events = []
        self.properties = []
        self.periods = set()

    def get_agg_short_name(
        self, aggregation: AggregationLiteral
    ) -> SQLAggregationLiteral | None:
        """Return the short name for a given attribute aggregation that is more fit to sql processing."""

        FEATURE_TYPE_SHORT_NAMES: dict[AggregationLiteral, SQLAggregationLiteral] = {
            "counter": "count",
            "sum": "sum",
            "min": "min",
            "max": "max",
            "first": "first",
            "last": "last",
            "unique_list": "unique_list",
        }
        return FEATURE_TYPE_SHORT_NAMES.get(aggregation, None)

    def get_cleaned_property_name(self, property: str) -> str:
        """Extracts the part after the colon or dot (:, .) in a property name and converts it to snake_case, otherwise it extracts the last bracketed value.

        Example:
        Input: "contexts_nl_basjes_yauaa_context_1[0]:deviceClass_last"
        Output: "device_class"

        Input: "contexts_nl_basjes_yauaa_context_1[0].deviceClass_last"
        Output: "device_class"
        """

        if not isinstance(property, str):
            return None

        if ":" in property:
            suffix = property.split(":")[1]
            # Convert to snake_case
            cleaned = re.sub(r"([a-z])([A-Z])", r"\1_\2", suffix).lower()
            if cleaned in (kw.lower() for kw in SQL_RESERVED_WORDS):
                cleaned += "_col"
            return cleaned
        elif "." in property:
            suffix = property.split(".")[-1]
            # Convert to snake_case
            cleaned = re.sub(r"([a-z])([A-Z])", r"\1_\2", suffix).lower()
            if cleaned in (kw.lower() for kw in SQL_RESERVED_WORDS):
                cleaned += "_col"
            return cleaned
        else:
            cleaned = property.lower()
            if cleaned in (kw.lower() for kw in SQL_RESERVED_WORDS):
                cleaned += "_col"
                return cleaned
            else:
                return property

    def add_to_properties(self, new_entry: Dict[str, str]):
        """Dynamically add a new property while ensuring deduplication to create a unique list of cleaned properties."""
        filtered_entry = {
            k: v
            for k, v in new_entry.items()
            if k not in {None, ""} and v not in {None, ""}
        }

        if not filtered_entry:
            return

        # Use a set to track unique dictionaries
        seen: Set[FrozenSet] = {frozenset(d.items()) for d in self.properties}

        frozen_entry = frozenset(filtered_entry.items())
        if frozen_entry not in seen:
            self.properties.append(filtered_entry)

    def resolve_property_name_collisions(self):
        seen = set()
        updated = []

        for entry in self.properties:
            for raw_key, cleaned in entry.items():
                if cleaned in seen:
                    base = cleaned
                    i = 2
                    while f"{base}_{i}" in seen:
                        i += 1
                    cleaned = f"{base}_{i}"
                seen.add(cleaned)
                updated.append({raw_key: cleaned})

        self.properties = updated

    def _get_full_event_reference_array(
        self, event_object_list: list[Event]
    ) -> list[str]:
        event_strings = []
        for event in event_object_list:
            event_str = f"iglu:{event.vendor}/{event.name}/jsonschema/{event.version}"
            event_strings.append(event_str)

        event_strings.sort()
        return event_strings

    def _get_filter_condition_name_component(self, filter_condition: Criterion) -> str:
        """Generate a SQL-friendly name component from a filter condition"""
        if not filter_condition:
            return ""

        operator_map = {
            "=": "eq",
            "!=": "neq",
            "<": "lt",
            ">": "gt",
            "<=": "lte",
            ">=": "gte",
            "like": "like",
        }

        property_name = self.get_cleaned_property_name(filter_condition.property)

        operator = operator_map.get(
            filter_condition.operator, filter_condition.operator
        )

        # Clean the value to be SQL-friendly
        value = str(filter_condition.value).lower()
        value = value.replace(" ", "_")
        value = value.replace("%", "pct")
        value = value.replace("-", "_")
        value = value.replace(".", "_")
        value = value.replace("/", "_")
        value = "".join(
            c for c in value if c.isalnum() or c == "_"
        )  # Remove any other special chars

        return f"{property_name}_{operator}_{value}"

    def _generate_column_name(
        self, attribute: AttributeOutput, agg_short_name: str
    ) -> str:
        """Generate a unique SQL-friendly column name incorporating filter conditions"""
        name_components = []

        # Start with type identifier to make the aggregation type clear
        name_components.append(agg_short_name)

        # Add attribute property if it exists
        if attribute.property:
            name_components.append(self.get_cleaned_property_name(attribute.property))

        # Add event filters
        for event in attribute.events:
            if not event.name:
                raise ValueError("Event name cannot be empty.")
            name_components.append(event.name)

        # Add filter conditions if they exist
        if attribute.criteria:
            filter_components = []

            # if any is not found use ALL, only one is allowed in the API
            combinator = "any" if attribute.criteria.any else "all"

            for condition in attribute.criteria.any or attribute.criteria.all or []:
                filter_components.append(
                    self._get_filter_condition_name_component(condition)
                )

            if filter_components:
                # Sort filter components to ensure consistent naming
                filter_components.sort()
                filter_name = f"_{combinator}_".join(filter_components)
                name_components.append(filter_name)

        # Join all components with underscores and ensure SQL-friendly
        column_name = "_".join(name_components)

        # replace hyphens with underscores
        column_name = column_name.replace("-", "_")

        # Remove any remaining special characters
        column_name = "".join(c for c in column_name if c.isalnum() or c == "_")
        # Ensure it doesn't start with a number
        if column_name[0].isdigit():
            column_name = f"n_{column_name}"
        if len(column_name) > 60:
            return attribute.name
        else:
            return column_name

    def _generate_modeling_steps(
        self, attribute: AttributeOutput
    ) -> list[ModelingStep]:
        """Generate 3 modeling steps based on attribute type and attributes defined as part of the JSON.
        Through looping through the attributes, events, properties and periods are also extracted.
        """
        # First add events and properties, they are needed for proper column reference for the steps
        self.events.extend(self._get_full_event_reference_array(attribute.events))
        if attribute.property:
            self.add_to_properties(
                {attribute.property: self.get_cleaned_property_name(attribute.property)}
            )
            self.resolve_property_name_collisions()
        if attribute.period is not None:
            self.periods.add(timedelta_isoformat(attribute.period))

        steps = []
        attribute_agg_short_name = self.get_agg_short_name(attribute.aggregation)
        if attribute_agg_short_name is None:
            raise ValueError(f"Unsupported aggregation: {attribute.aggregation}")

        # Step 1: Filtered events setup
        steps.append(
            ModelingStep(
                step_type="filtered_events",
                enabled=False,
                aggregation=None,
                column_name=next(
                    (
                        v
                        for d in self.properties
                        for k, v in d.items()
                        if k == attribute.property
                    ),
                    None,
                ),  # Get the cleaned column name for a given raw property key from the list of property mappings. Returns None if the key is not found.
                modeling_criteria=None,
            )
        )

        # Step 2: Daily Agg level
        criteria = ModelingCriteria()
        column_name = None
        event_condition_array = []
        modified_conditions = []

        # Define an artificial filter condition based on the list of events
        for event in attribute.events:
            if event.name is None:
                raise ValueError("Event name cannot be None")
            event_condition_array.append("'" + event.name + "'")

        event_condition = FilterCondition(
            property="event_name",
            operator="in",
            value=",".join(event_condition_array),
        )
        criteria.add_condition(condition=event_condition, target_group="all")

        # Get all the original conditions
        original_criteria = attribute.criteria
        if original_criteria:
            combinator: Literal["all", "any"] | None = (
                "all"
                if original_criteria.all
                else "any" if original_criteria.any else None
            )
            conditions = original_criteria.all or original_criteria.any or []

            # Loop through to clean up the property name (to be able to reference the unnested filtered event column)
            for condition in conditions:
                modified_condition = FilterCondition(**condition.model_dump())
                modified_condition.property = self.get_cleaned_property_name(
                    modified_condition.property
                )
                self.add_to_properties(
                    {
                        condition.property: self.get_cleaned_property_name(
                            condition.property
                        )
                    }
                )
                modified_conditions.append(modified_condition)
            criteria.add_conditions(
                conditions=[mc for mc in modified_conditions],
                target_group=combinator,
            )
        # Generate column name based on attribute aggregation
        if attribute_agg_short_name in ["first", "last"]:
            # For first/last, use the property name directly
            if attribute.property is None:
                raise ValueError("Property cannot be None for first/last aggregation")
            column_name = f"{attribute_agg_short_name}_{self.get_cleaned_property_name(attribute.property)}"
        else:
            # For other aggregation types (count, sum, etc), use the full column name generation
            column_name = self._generate_column_name(
                attribute, attribute_agg_short_name
            )

        steps.append(
            ModelingStep(
                step_type="daily_aggregation",
                enabled=True,
                aggregation=attribute_agg_short_name,
                column_name=column_name,
                modeling_criteria=criteria,
            )
        )

        # Step 3: Feature Agg level
        criteria = ModelingCriteria()

        # Need to correct counts to sum in the final agg level
        if attribute_agg_short_name == "count":
            attribute_agg_short_name = "sum"

        # Get last n day type filters, they need artificial condition
        if attribute.period is not None:
            criteria.add_condition(
                condition=FilterCondition(
                    property="period",
                    operator=">",
                    value=attribute.period.days,
                ),
                target_group="all",
            )

        steps.append(
            ModelingStep(
                step_type="attribute_aggregation",
                enabled=True,
                aggregation=attribute_agg_short_name,
                column_name=attribute.name,
                modeling_criteria=criteria,
            )
        )

        new_events = self._get_full_event_reference_array(attribute.events)
        # Use dict.fromkeys to maintain order while deduplicating
        self.events = list(dict.fromkeys(self.events + new_events))
        if attribute.property:
            self.add_to_properties(
                {attribute.property: self.get_cleaned_property_name(attribute.property)}
            )
        if attribute.period is not None:
            self.periods.add(timedelta_isoformat(attribute.period))

        return steps

    def create_base_config(self) -> DbtBaseConfig:
        """
        Process attribute definitions and return the base config format (this would eventually allow for users to make changes, if needed).
        """

        attributes = self.data.attributes or []
        transformed_attributes = [
            [step for step in self._generate_modeling_steps(attribute)]
            for attribute in attributes
        ]
        return DbtBaseConfig(
            events=[item for item in self.events if item not in {None, ""}],
            properties=self.properties,
            periods=[item for item in self.periods if item not in {None, ""}],
            transformed_attributes=transformed_attributes,
            entity_key=self.data.entity_key,
        )
