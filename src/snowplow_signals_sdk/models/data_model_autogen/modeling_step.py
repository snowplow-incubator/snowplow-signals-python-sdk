from pydantic import BaseModel, Field as PydanticField
from typing import List, Optional, Dict, Any, Literal


class FilterCondition(BaseModel):
    property: str = PydanticField(
        description="The path to the property on the event or entity or the specific column in the upstream modelling aggregate layer you wish to filter."
    )
    operator: Literal[
        "equals",
        "not_equals",
        "less_than",
        "greater_than",
        "less_than_or_equal",
        "like",
        "exists",
    ] = PydanticField(
        description="The operator used to compare the property to the value."
    )
    value: str | int | float | bool = PydanticField(
        description="The value to compare the property to."
    )


class FilterCombinator(BaseModel):
    combinator: Literal["and", "or"] = PydanticField(
        description="The logical operator used to combine the conditions."
    )
    condition: list[FilterCondition] = PydanticField(
        description="An array of conditions used to filter the events, or the appropriate modeling step."
    )


class ModelingStep(BaseModel):
    step_type: Literal["filtered_events", "daily_aggregation", "feature_aggregation"]
    enabled: bool = (
        True  # Whether the user would like to materialize that level of aggregation
    )
    type: Literal["count", "sum", "min", "max", "avg", "first", "last"] | None = (
        PydanticField(description="The calculation type of the feature.")
    )
    column_name: str | None = PydanticField(
        description="The column name of the feature",
        default=None,
    )
    filter: FilterCombinator | None = PydanticField(
        description="Filter combinators and a list of conditions to apply to the given modeling level.",
        default=None,
    )
