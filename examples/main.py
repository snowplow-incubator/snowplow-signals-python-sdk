from pydantic import ValidationError

from .features import (
    AverageProductPrice,
    CheapProductsCount,
    ExpensiveProductsCount,
    LastCartValue,
    MaxCartValue,
    MinCartValue,
    TotalProductPrice,
    UniqueProductNames,
)
from snowplow_signals.models.data_source import DataSource
from snowplow_signals.models.entity import Entity
from snowplow_signals.models.feature import (
    Feature,
    FilterCombinator,
    FilterCondition,
)
from snowplow_signals.models.feature_service import FeatureService
from snowplow_signals.models.feature_view import FeatureView
from snowplow_signals.signals import Signals


def main():
    sp_signals = Signals()

    add_to_cart_count_feature = Feature(
        name="add_to_cart_events_count",
        dtype="INT32",
        events=[
            "iglu:com.snowplowanalytics.snowplow.ecommerce/snowplow_ecommerce_action/jsonschema/1-0-2"
        ],
        type="counter",
        filter=FilterCombinator(
            combinator="and",
            condition=[
                FilterCondition(
                    property="event.type", operator="equals", value="add_to_cart"
                )
            ],
        ),
    )
    session_entity = Entity(name="session")

    fv = FeatureView(
        entities=[session_entity],
        name="new_feature_views",
        version=1,
        features=[add_to_cart_count_feature],
        status="Live",
    )

    fs = FeatureService(name="new_fs", feature_views=[fv])

    sp_signals.apply(objects=[fs])


if __name__ == "__main__":
    main()
