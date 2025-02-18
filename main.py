from pydantic import ValidationError

from snowplow_signals_sdk.features import (
    AverageProductPrice,
    CheapProductsCount,
    ExpensiveProductsCount,
    LastCartValue,
    MaxCartValue,
    MinCartValue,
    TotalProductPrice,
    UniqueProductNames,
)
from snowplow_signals_sdk.models.feast.data_source import DataSource
from snowplow_signals_sdk.models.feast.entity import Entity
from snowplow_signals_sdk.models.feast.feature_service import FeatureService
from snowplow_signals_sdk.models.feast.feature_view import FeatureView
from snowplow_signals_sdk.models.feature import (
    Feature,
    FilterCombinator,
    FilterCondition,
)
from snowplow_signals_sdk.signals_store import SignalsStore


def main():
    sp_signals = SignalsStore()

    add_to_cart_count_feature = Feature(
        name="add_to_cart_events_count",
        scope="session",
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

    fv = FeatureView(
        entities=["67b37d73a788623ecc4f49c0"],
        name="new_feature_views",
        version=1,
        features=[add_to_cart_count_feature],
        status="Live",
    )

    fs = FeatureService(name="new_fs", feature_views=[fv])

    sp_signals.apply(objects=[fs])


if __name__ == "__main__":
    main()


# curl -X POST "http://localhost:8000/api/v1/registry/feature_services" \
#      -H "Content-Type: application/json" \
#      -d '{
#           "name": "user_feature_service",
#           "features_views": [ "user_behavior_features" ],
#           "description": "Feature service for user analytics"
#      }'
