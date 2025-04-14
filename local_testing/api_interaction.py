import os
from snowplow_signals import Signals, View, user_entity, session_entity, Attribute, Event, BatchSource

def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Environment variable {name} is not set")
    return value

def main():
    # Initialize the Signals client
    sp_signals = Signals(
        api_url=get_env_var("SNOWPLOW_API_URL"),
        api_key=get_env_var("SNOWPLOW_API_KEY"),
        api_key_id=get_env_var("SNOWPLOW_API_KEY_ID"),
        org_id=get_env_var("SNOWPLOW_ORG_ID")
    )

    # # Create batch source
    # batch_source = BatchSource(
    #     name="my_transaction_interactions_source",
    #     database="SNOWPLOW_DEV1",
    #     table="SNOWPLOW_ECOMMERCE_TRANSACTION_INTERACTIONS_FEATURES",
    #     timestamp_field="UPDATED_AT"
    # )

    # Create features
    last_geo_country = Attribute(
        name="last_geo_country",
        type="string",
        description="Last geo_country value in the last 8 days",
        events=[Event(vendor="com.snowplowanalytics.snowplow", name="page_view", version="1-0-0")],
        aggregation="last",
        property="geo_country",
        property_syntax="snowflake",
        criteria=None,
        period=None
    )

    page_view_count = Attribute(
        name="page_view_count_last_7_days",
        type="int64",
        description="Count of page views in the last 7 days",
        events=[Event(vendor="com.snowplowanalytics.snowplow", name="page_view", version="1-0-0")],
        aggregation="counter",
        property=None,
        property_syntax="snowflake",
        criteria=None,
        period="P7D"
    )

    # Create feature view
    view = View(
        name="my_transaction_interactions_features",
        version=1,
        entity=user_entity,
        ttl=None,
        batch_source=None,
        online=True,
        description="My transaction interactions features",
        tags=None,
        owner=None,
        fields=None,
        attributes=[last_geo_country, page_view_count]
    )

    print("Applying feature view...")
    applied = sp_signals.apply([view])
    print(f"Applied {len(applied)} objects")

    # Get all views
    print("\nFetching all views...")
    all_views = sp_signals.registry.api_client.make_request(
        method="GET",
        endpoint="registry/views/",
        params={"offline": True}
    )
    print(f"Found {len(all_views)} views")

    # Print view details
    for view in all_views:
        print(f"\nView: {view['name']} (v{view['version']})")
        print(f"Entity: {view['entity']['name']}")
        if view.get('attributes'):
            print("Attributes:")
            for attr in view['attributes']:
                print(f"  - {attr['name']} ({attr['type']})")

if __name__ == "__main__":
    main()