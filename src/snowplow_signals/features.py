from typing import List, Literal, Optional

from .models.feature import Feature, FilterCombinator, FilterCondition


class AddToCartCountFeature(Feature):
    name: str = "add_to_cart_events_count"
    scope: str = "session"
    events: List[str] = [
        "iglu:com.snowplowanalytics.snowplow.ecommerce/snowplow_ecommerce_action/jsonschema/1-0-2"
    ]
    type: Literal["counter"] = "counter"
    property: Optional[str] = None
    filter: Optional[str] = FilterCombinator(
        combinator="and",
        condition=[
            FilterCondition(
                property="event.type", operator="equals", value="add_to_cart"
            )
        ],
    )
    signals_derived: bool = False


class AverageProductPrice(Feature):
    name: str = "avg_product_price"
    scope: str = "session"
    events: List[str] = [
        "iglu:com.snowplowanalytics.snowplow.ecommerce/snowplow_ecommerce_action/jsonschema/1-0-2"
    ]
    type: Literal["aggregation(avg)"] = "aggregation(avg)"
    property: str = (
        "contexts_com_snowplowanalytics_snowplow_ecommerce_product_1_0_0.price"
    )
    filter: Optional[str] = FilterCombinator(
        combinator="and",
        condition=[
            FilterCondition(
                property="event.type", operator="equals", value="add_to_cart"
            )
        ],
    )
    signals_derived: bool = False


class LastCartValue(Feature):
    name: str = "last_cart_value"
    scope: str = "session"
    events: List[str] = [
        "iglu:com.snowplowanalytics.snowplow.ecommerce/snowplow_ecommerce_action/jsonschema/1-0-2"
    ]
    type: Literal["last"] = "last"
    property: str = (
        "contexts_com_snowplowanalytics_snowplow_ecommerce_cart_1_0_0.total_value"
    )
    filter: Optional[str] = FilterCombinator(
        combinator="and",
        condition=[
            FilterCondition(
                property="event.type", operator="equals", value="add_to_cart"
            )
        ],
    )
    signals_derived: bool = False


class MaxCartValue(Feature):
    name: str = "max_cart_value"
    scope: str = "session"
    events: List[str] = [
        "iglu:com.snowplowanalytics.snowplow.ecommerce/snowplow_ecommerce_action/jsonschema/1-0-2"
    ]
    type: Literal["aggregation(max)"] = "aggregation(max)"
    property: str = (
        "contexts_com_snowplowanalytics_snowplow_ecommerce_cart_1_0_0.total_value"
    )
    filter: Optional[str] = FilterCombinator(
        combinator="and",
        condition=[
            FilterCondition(
                property="event.type", operator="equals", value="add_to_cart"
            )
        ],
    )
    signals_derived: bool = False


class MinCartValue(Feature):
    name: str = "min_cart_value"
    scope: str = "session"
    events: List[str] = [
        "iglu:com.snowplowanalytics.snowplow.ecommerce/snowplow_ecommerce_action/jsonschema/1-0-2"
    ]
    type: Literal["aggregation(min)"] = "aggregation(min)"
    property: str = (
        "contexts_com_snowplowanalytics_snowplow_ecommerce_cart_1_0_0.total_value"
    )
    filter: Optional[str] = FilterCombinator(
        combinator="and",
        condition=[
            FilterCondition(
                property="event.type", operator="equals", value="add_to_cart"
            )
        ],
    )
    signals_derived: bool = False


class TotalProductPrice(Feature):
    name: str = "total_product_price"
    scope: str = "session"
    events: List[str] = [
        "iglu:com.snowplowanalytics.snowplow.ecommerce/snowplow_ecommerce_action/jsonschema/1-0-2"
    ]
    type: Literal["aggregation(sum)"] = "aggregation(sum)"
    property: str = "contexts_com_snowplowanalytics_snowplow_ecommerce_cart_1_0_0.price"
    filter: Optional[str] = FilterCombinator(
        combinator="and",
        condition=[
            FilterCondition(
                property="event.type", operator="equals", value="add_to_cart"
            )
        ],
    )
    signals_derived: bool = False


class UniqueProductNames(Feature):
    name: str = "unique_product_names"
    scope: str = "session"
    events: List[str] = [
        "iglu:com.snowplowanalytics.snowplow.ecommerce/snowplow_ecommerce_action/jsonschema/1-0-2"
    ]
    type: Literal["unique_list"] = "unique_list"
    property: str = "contexts_com_snowplowanalytics_snowplow_ecommerce_cart_1_0_0.name"
    filter: Optional[str] = FilterCombinator(
        combinator="and",
        condition=[
            FilterCondition(
                property="event.type", operator="equals", value="add_to_cart"
            )
        ],
    )
    signals_derived: bool = False


class ExpensiveProductsCount(Feature):
    name: str = "expensive_products_count"
    scope: str = "session"
    events: List[str] = [
        "iglu:com.snowplowanalytics.snowplow.ecommerce/snowplow_ecommerce_action/jsonschema/1-0-2"
    ]
    type: Literal["counter"] = "counter"
    filter: Optional[str] = FilterCombinator(
        combinator="and",
        condition=[
            FilterCondition(
                property="event.type", operator="equals", value="add_to_cart"
            ),
            FilterCondition(
                property="contexts_com_snowplowanalytics_snowplow_ecommerce_product_1_0_0.price",
                operator="greater_than",
                value=100,
            ),
        ],
    )
    signals_derived: bool = False


class CheapProductsCount(Feature):
    name: str = "cheap_products_count"
    scope: str = "session"
    events: List[str] = [
        "iglu:com.snowplowanalytics.snowplow.ecommerce/snowplow_ecommerce_action/jsonschema/1-0-2"
    ]
    type: Literal["counter"] = "counter"
    filter: Optional[str] = FilterCombinator(
        combinator="and",
        condition=[
            FilterCondition(
                property="event.type", operator="equals", value="add_to_cart"
            ),
            FilterCondition(
                property="contexts_com_snowplowanalytics_snowplow_ecommerce_product_1_0_0.price",
                operator="less_than",
                value=100,
            ),
        ],
    )
    signals_derived: bool = False
