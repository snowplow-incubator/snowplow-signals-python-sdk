from typing import Literal
from datetime import timedelta

from pydantic import BaseModel
from pydantic import Field as PydanticField

from snowplow_signals.models.field import Field


class FilterCondition(BaseModel):
    property: str = PydanticField(
        description="The path to the property on the event or entity you wish to filter."
    )
    operator: Literal[
        "equals",
        "not_equals",
        "less_than",
        "greater_than",
        "less_than_or_equal",
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
        description="An array of conditions used to filter the events."
    )


class Feature(Field):
    events: list[str] = PydanticField(
        description="An array of events used to calculate this trait.",
        min_length=1,
    )
    type: Literal[
        "counter",
        "aggregation(sum)",
        "aggregation(min)",
        "aggregation(max)",
        "aggregation(avg)",
        "most_frequent",
        "least_frequent",
        "first",
        "last",
        "unique_list",
        "unique_list_count",
        "funnel",
    ] = PydanticField(description="The calculation type of the feature.")

    property: str | None = PydanticField(
        description="The path (or dropdown) to the property on the event or entity you wish to calculate. If multiple events are selected this property must be in the same location.",
        default=None,
    )

    filter: FilterCombinator | None = PydanticField(
        description="A filter condition to apply to the events.",
        default=None,
    )

    signals_derived: bool = PydanticField(
        description="Determines if the trait should be inferred from signals",
        default=False,
    )

    period: timedelta | None = PydanticField(
        description="Defines the time period, further refining the scope of the feature.",
        default=None,
    )
