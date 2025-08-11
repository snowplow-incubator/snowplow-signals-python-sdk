from typing import Literal

from pydantic import BaseModel


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


class FilteredEventsProperty(BaseModel):
    type: str
    full_path: str
    alias: str
    column_prefix: str | None = None


class FilteredEvents(BaseModel):
    events: list[ConfigEvents]
    properties: list[FilteredEventsProperty] | None = None


class DbtConfig(BaseModel):
    filtered_events: FilteredEvents
    daily_agg: DailyAggregations
    attributes: ConfigAttributes


SQLConditions = Literal["and", "or"]
