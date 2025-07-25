from abc import ABC, abstractmethod
from re import sub

from pydantic import BaseModel, ConfigDict, Field


def _clean_vendor(vendor: str) -> str:
    # see https://github.com/snowplow/snowplow-python-analytics-sdk/blob/0ddca91e3f6d8bed88627fa557790aa4868bdace/snowplow_analytics_sdk/json_shredder.py#L64
    return vendor.replace(".", "_").lower()


def _clean_name(name: str) -> str:
    # see https://github.com/snowplow/snowplow-python-analytics-sdk/blob/0ddca91e3f6d8bed88627fa557790aa4868bdace/snowplow_analytics_sdk/json_shredder.py#L65
    return sub(r"([^A-Z_])([A-Z])", r"\g<1>_\g<2>", name).lower()


def _clean_version(version: int) -> str:
    # see https://github.com/snowplow/snowplow-python-analytics-sdk/blob/0ddca91e3f6d8bed88627fa557790aa4868bdace/snowplow_analytics_sdk/json_shredder.py#L66
    return str(version)


class BaseProperty(BaseModel, ABC):
    @abstractmethod
    def _to_api_property(self) -> str:
        """
        Converts the property to a format suitable for API requests.
        """
        pass


class BaseSDJProperty(BaseProperty, ABC):
    model_config = ConfigDict(regex_engine="python-re")

    vendor: str = Field(description="The vendor of the property.", min_length=1)
    name: str = Field(
        description="The name of the property.",
        min_length=1,
        pattern=r"^[a-zA-Z0-9-_]+$",
        max_length=128,
    )
    major_version: int = Field(description="The major version of the property.")
    path: str = Field(
        min_length=1,
        # Exclude "$" only character.
        # Exclude array notation field access like ['field'] or ["field"] until we fully support it.
        pattern=r"^(?!\$$)(?!.*\[['\"]).+$",
        description="The path to the attribute targeted. Allows for direct dot (.) notation and index ([n]) access. Uses a subset of JSONPath syntax without requiring the leading '$.' root access. E.g. 'user.profile.name' or 'events[0].items[1].value'.",
    )
    """The path to the attribute targeted. Allows for direct dot (.) notation and index ([n]) access. Uses a subset of JSONPath syntax without requiring the leading '$.' root access.
        E.g. 'user.profile.name' or 'events[0].items[1].value'."""
