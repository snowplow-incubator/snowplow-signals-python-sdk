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

    data_source = DataSource(
        name="custom_unified_users_source",
        type="snowflake",
        database="SNOWPLOW_DEV1",
        schema="SIGNALS",
        table="SNOWPLOW_UNIFIED_USERS_FEATURES",
        timestamp_field="UPDATED_AT",
    )

    feature_view = FeatureView(
        name="user_behavior_features",
        features=[add_to_cart_count_feature],
    )
    feature_service = FeatureService(name="new_fs", feature_views=[feature_view])

    online_features_df = sp_signals.get_online_features(
        features=feature_service, entity_type_id="domain_userid"
    ).to_dataframe()
    print(online_features_df)


if __name__ == "__main__":
    main()
