from functools import wraps
from re import sub
from typing import Literal, TypeAlias

from pydantic import BaseModel, Field, RootModel

from .wrappers.criteria import Criteria, Criterion

AtomicField: TypeAlias = Literal[
    "app_id",
    "platform",
    "etl_tstamp",
    "collector_tstamp",
    "dvce_created_tstamp",
    "event",
    "event_id",
    "txn_id",
    "name_tracker",
    "v_tracker",
    "v_collector",
    "v_etl",
    "user_id",
    "user_ipaddress",
    "user_fingerprint",
    "domain_userid",
    "domain_sessionidx",
    "network_userid",
    "geo_country",
    "geo_region",
    "geo_city",
    "geo_zipcode",
    "geo_latitude",
    "geo_longitude",
    "geo_region_name",
    "ip_isp",
    "ip_organization",
    "ip_domain",
    "ip_netspeed",
    "page_url",
    "page_title",
    "page_referrer",
    "page_urlscheme",
    "page_urlhost",
    "page_urlport",
    "page_urlpath",
    "page_urlquery",
    "page_urlfragment",
    "refr_urlscheme",
    "refr_urlhost",
    "refr_urlport",
    "refr_urlpath",
    "refr_urlquery",
    "refr_urlfragment",
    "refr_medium",
    "refr_source",
    "refr_term",
    "mkt_medium",
    "mkt_source",
    "mkt_term",
    "mkt_content",
    "mkt_campaign",
    "contexts",
    "se_category",
    "se_action",
    "se_label",
    "se_property",
    "se_value",
    "unstruct_event",
    "tr_orderid",
    "tr_affiliation",
    "tr_total",
    "tr_tax",
    "tr_shipping",
    "tr_city",
    "tr_state",
    "tr_country",
    "ti_orderid",
    "ti_sku",
    "ti_name",
    "ti_category",
    "ti_price",
    "ti_quantity",
    "pp_xoffset_min",
    "pp_xoffset_max",
    "pp_yoffset_min",
    "pp_yoffset_max",
    "useragent",
    "br_name",
    "br_family",
    "br_version",
    "br_type",
    "br_renderengine",
    "br_lang",
    "br_features_pdf",
    "br_features_flash",
    "br_features_java",
    "br_features_director",
    "br_features_quicktime",
    "br_features_realplayer",
    "br_features_windowsmedia",
    "br_features_gears",
    "br_features_silverlight",
    "br_cookies",
    "br_colordepth",
    "br_viewwidth",
    "br_viewheight",
    "os_name",
    "os_family",
    "os_manufacturer",
    "os_timezone",
    "dvce_type",
    "dvce_ismobile",
    "dvce_screenwidth",
    "dvce_screenheight",
    "doc_charset",
    "doc_width",
    "doc_height",
    "tr_currency",
    "tr_total_base",
    "tr_tax_base",
    "tr_shipping_base",
    "ti_currency",
    "ti_price_base",
    "base_currency",
    "geo_timezone",
    "mkt_clickid",
    "mkt_network",
    "etl_tags",
    "dvce_sent_tstamp",
    "refr_domain_userid",
    "refr_device_tstamp",
    "derived_contexts",
    "domain_sessionid",
    "derived_tstamp",
    "event_vendor",
    "event_name",
    "event_format",
    "event_version",
    "event_fingerprint",
    "true_tstamp",
]


def _clean_vendor(vendor: str) -> str:
    # see https://github.com/snowplow/snowplow-python-analytics-sdk/blob/0ddca91e3f6d8bed88627fa557790aa4868bdace/snowplow_analytics_sdk/json_shredder.py#L64
    return vendor.replace(".", "_").lower()


def _clean_name(name: str) -> str:
    # see https://github.com/snowplow/snowplow-python-analytics-sdk/blob/0ddca91e3f6d8bed88627fa557790aa4868bdace/snowplow_analytics_sdk/json_shredder.py#L65
    return sub(r"([^A-Z_])([A-Z])", r"\g<1>_\g<2>", name).lower()


def _clean_version(version: str | int) -> str:
    # see https://github.com/snowplow/snowplow-python-analytics-sdk/blob/0ddca91e3f6d8bed88627fa557790aa4868bdace/snowplow_analytics_sdk/json_shredder.py#L66
    return str(version) if isinstance(version, int) else version.partition("-")[0]


def _default_criteria(
    property: str, operator, other: str | int | float | bool | list
) -> Criteria:
    return Criteria(
        all=[
            Criterion(
                property=property,
                operator=operator,
                value=other,
                property_syntax="snowflake",
            ),
        ],
        any=None,
    )


class EntityProperty(BaseModel):
    """Reference a nested property from an entity field from the event context."""

    vendor: str
    name: str
    path: str = ""
    version: str | int = Field(default=1, pattern=r"^\d+-\d+-\d+$")
    index: int = 0

    def __str__(self) -> str:
        path = "" if not self.path else f".{self.path}"
        return f"contexts_{_clean_vendor(self.vendor)}_{_clean_name(self.name)}_{_clean_version(self.version)}[{self.index}]{path}"


class SelfDescProperty(BaseModel):
    """Reference a nested property from a Self-Describing event field."""

    vendor: str
    name: str
    path: str = ""
    version: str | int = Field(default=1, pattern=r"^\d+-\d+-\d+$")

    def __str__(self) -> str:
        path = "" if not self.path else f":{self.path}"
        return f"unstruct_event_{_clean_vendor(self.vendor)}_{_clean_name(self.name)}_{_clean_version(self.version)}{path}"


class Column(RootModel[AtomicField | EntityProperty | SelfDescProperty]):
    """Provide syntax sugar for creating Criterion instances from field references."""

    @staticmethod
    def atomic(field: AtomicField) -> "Column":
        return Column(field)

    @staticmethod
    @wraps(SelfDescProperty)
    def event(*args, **kwargs) -> "Column":
        return Column(SelfDescProperty(*args, **kwargs))

    @staticmethod
    @wraps(EntityProperty)
    def entity(*args, **kwargs) -> "Column":
        return Column(EntityProperty(*args, **kwargs))

    def __str__(self) -> str:
        return str(self.root)

    def __getitem__(self, key) -> "Column":
        if isinstance(self.root, str):
            raise KeyError()
        return Column(self.root.model_copy(update={"path": key}))

    def __eq__(self, other):
        if isinstance(other, (str, int, float, bool, list)):
            return _default_criteria(str(self), "=", other)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, (str, int, float, bool, list)):
            return _default_criteria(str(self), "!=", other)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, (int, float)):
            return _default_criteria(str(self), "<", other)
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, (int, float)):
            return _default_criteria(str(self), ">", other)
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, (int, float)):
            return _default_criteria(str(self), "<=", other)
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, (int, float)):
            return _default_criteria(str(self), ">=", other)
        return NotImplemented

    def __mod__(self, other):
        if isinstance(other, str):
            return _default_criteria(str(self), "like", other)
        return NotImplemented

    def __lshift__(self, other):
        if isinstance(other, list):
            return _default_criteria(str(self), "in", other)
        return NotImplemented
