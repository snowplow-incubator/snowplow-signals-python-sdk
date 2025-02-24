from typing import Dict, Any, List, Set, FrozenSet
from pydantic import BaseModel
from models.data_model_autogen.modeling_step import (
    ModelingStep,
    FilterCombinator,
    FilterCondition,
)
import re


class OverviewConfigGenerator(BaseModel):
    data: Dict[str, Any]
    events: Set[str] = set()
    properties: List[dict[str, str]] = []
    event_names: Set[str] = set()
    periods: Set[str] = set()

    def get_type_short_name(self, feature_type: str) -> str:
        """Return the short name for a given feature type."""

        FEATURE_TYPE_SHORT_NAMES = {
            "counter": "count",
            "aggregation(sum)": "sum",
            "aggregation(min)": "min",
            "aggregation(max)": "max",
            "first": "first",
            "last": "last",
        }
        return FEATURE_TYPE_SHORT_NAMES.get(feature_type, "not_found")

    def get_cleaned_property_name(self, property: str) -> str:
        """Extracts the part after the colon (:) in a property name and converts it to snake_case.

        Example:
        Input: "contexts_nl_basjes_yauaa_context_1[0]:deviceClass_last"
        Output: "device_class"
        """
        if property is None or ":" not in property:
            return property

        # Extract suffix after ':'
        suffix = property.split(":")[-1]

        # Convert to snake_case
        return re.sub(r"([a-z])([A-Z])", r"\1_\2", suffix).lower()

    def add_property(self, new_entry: Dict[str, str]):
        """Dynamically add a new property while ensuring deduplication."""
        filtered_entry = {
            k: v
            for k, v in new_entry.items()
            if k not in {None, ""} and v not in {None, ""}
        }

        if not filtered_entry:  # Skip empty entries
            return

        # Use a set to track unique dictionaries
        seen: Set[FrozenSet] = {frozenset(d.items()) for d in self.properties}

        frozen_entry = frozenset(filtered_entry.items())
        if frozen_entry not in seen:
            self.properties.append(filtered_entry)

    def _generate_modeling_steps(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate modeling steps based on feature type and attributes defined as part of the JSON.
        """
        steps = []
        # print(f"Feature Type Short Name: {feature["type"]}")

        # Expecting the SDK to prevent letting users define unsupported batch features upfront
        feature_type_short_name = self.get_type_short_name(feature["type"])
        if feature_type_short_name == "not_found":
            raise ValueError(f"Unsupported feature type: {feature['type']}")

        # Step 1: Always apply a filtered_events step, based on events specified
        # TODO: hardcode filtering out page_pings events and/ or find a way to block generation that way)

        # Assume no filtered events table is needed until we find a filter condition later
        steps.append(
            ModelingStep(
                step_type="filtered_events",
                enabled=False,
                type=None,
                column_name=None,
                filter=None,
            )
        )

        # Step 2: Daily Agg level

        # Attempt creating a unique name of column automatically based on filter conditions
        daily_agg_name_components = []
        type_short_name = self.get_type_short_name(feature["type"])

        if feature.get("filter", None) is not None:
            combinator = feature["filter"].get("combinator", "and")
            conditions = feature["filter"].get("condition", [])

            modified_conditions = []
            for condition in conditions:
                modified_condition = FilterCondition(**condition)

                # If there is an event.type condition, modify the appropriate levels (filtered_events, daily_agg, feature_agg)
                if modified_condition.property == "event.type":
                    daily_agg_name_components.append(str(condition["value"]))
                    if steps[0].filter is None:
                        steps[0].filter = FilterCombinator(
                            combinator="and",
                            condition=[
                                FilterCondition(
                                    property="event_name",
                                    operator="equals",
                                    value=condition["value"],
                                )
                            ],
                        )
                    else:
                        steps[0].filter.condition.append(
                            FilterCondition(
                                property="event_name",
                                operator="equals",
                                value=condition["value"],
                            )
                        )
                    steps[0].enabled = True
                    self.event_names.add(condition["value"])
                    modified_condition.property = "event_name"
                else:
                    if feature["property"] is not None:
                        agg_filter = FilterCombinator(
                            combinator="and",
                            condition=[
                                FilterCondition(
                                    property=feature["property"],
                                    operator="exists",
                                    value=True,
                                )
                            ],
                        )

                modified_conditions.append(modified_condition)

            # Store the modified conditions in the dictionary
            agg_filter = FilterCombinator(
                combinator=combinator, condition=modified_conditions
            )

            if feature.get("property", None) is not None:
                column_name = "_".join(
                    [
                        "_{}_".format(combinator).join(daily_agg_name_components),
                        type_short_name,
                        self.get_cleaned_property_name(feature["property"]),
                    ]
                )
            else:
                column_name = "_".join(
                    [
                        "_{}_".format(combinator).join(daily_agg_name_components),
                        type_short_name,
                    ]
                )
        else:
            agg_filter = None
            if feature.get("property", None) is not None:
                column_name = "_".join(
                    [
                        self.get_cleaned_property_name(feature["property"]),
                        type_short_name,
                    ]
                )
            else:
                column_name = type_short_name

        # Construct and return the new ModelingStep with the modified filter
        steps.append(
            ModelingStep(
                step_type="daily_aggregation",
                enabled=True,
                type=type_short_name,
                column_name=column_name,
                filter=agg_filter,
            )
        )

        # Step 3: Feature Agg level
        steps.append(
            ModelingStep(
                step_type="feature_aggregation",
                enabled=True,
                type=type_short_name,
                column_name=feature["name"],
                filter=None,
            )
        )

        # Add to sets
        self.events.update(feature["events"])
        self.add_property(
            {feature["property"]: self.get_cleaned_property_name(feature["property"])}
        )
        (
            self.periods.update(feature["period"])
            if feature["period"] is not None
            else None
        )

        return steps

    def get_base_config(self) -> Dict[str, Any]:
        with open("utils/example_batch_features.json") as f:
            return json.load(f)

    def create_config_overview(self) -> Dict[str, Any]:
        """
        Process feature definitions and return the config overview format (this would eventually allow for users to make changes, if needed).
        """
        features = self.data.get("features", [])
        transformed_features = [
            self._generate_modeling_steps(feature) for feature in features
        ]

        return {
            "events": [item for item in self.events if item not in {None, ""}],
            "properties": self.properties,
            "event_names": [
                item for item in self.event_names if item not in {None, ""}
            ],
            "periods": [item for item in self.periods if item not in {None, ""}],
            "transformed_features": [
                [step.model_dump() for step in feature_steps]
                for feature_steps in transformed_features
            ],
        }
