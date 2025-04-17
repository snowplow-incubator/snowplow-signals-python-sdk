from typing import Literal

from pydantic import BaseModel
from pydantic import Field as PydanticField


class FilterCondition(BaseModel):
    property: str = PydanticField(
        description="The path to the property on the event or entity or the specific column in the upstream modelling aggregate layer you wish to filter."
    )
    operator: Literal[
        "=",
        "!=",
        "<",
        ">",
        "<=",
        ">=",
        "like",
        "in",
    ] = PydanticField(
        description="The operator used to compare the property to the value."
    )
    value: str | int | float | bool = PydanticField(
        description="The value to compare the property to."
    )


class ModelingCriteria(BaseModel):
    all: list[FilterCondition] = PydanticField(default_factory=list)
    any: list[FilterCondition] = PydanticField(default_factory=list)

    def add_condition(
        self, condition: FilterCondition, target_group: Literal["all", "any"]
    ):
        if target_group == "all":
            self.all.append(condition)
        elif target_group == "any":
            self.any.append(condition)
        else:
            raise ValueError("target_group must be 'all' or 'any'")

    def add_conditions(
        self,
        conditions: list[FilterCondition],
        target_group: Literal["all", "any"] | None,
    ):
        if target_group == "all":
            if self.all:
                self.all.extend(conditions)
            else:
                self.all = conditions
        elif target_group == "any":
            if self.any:
                self.any.extend(conditions)
            else:
                self.any = conditions
        else:
            raise ValueError("target_group must be 'all' or 'any'")


class ModelingStep(BaseModel):
    step_type: Literal["filtered_events", "daily_aggregation", "attribute_aggregation"]
    enabled: bool = (
        True  # Whether the user would like to materialize that level of aggregation
    )
    aggregation: (
        Literal["count", "sum", "min", "max", "avg", "first", "last", "unique_list"]
        | None
    ) = PydanticField(description="The calculation type of the attribute.")
    column_name: str | None = PydanticField(
        description="The column name of the attribute",
        default=None,
    )
    modeling_criteria: ModelingCriteria | None = PydanticField(
        description="A list of AND (all) and OR (any) conditions to apply to the given modeling level filtering.",
        default=None,
    )
