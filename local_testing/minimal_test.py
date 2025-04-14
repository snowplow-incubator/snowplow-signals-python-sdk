import os
from snowplow_signals import Signals, View, user_entity, session_entity, Attribute, Event, BatchSource

def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Environment variable {name} is not set")
    return value

def main():
    # Initialize client
    sp_signals = Signals(
        api_url=get_env_var("SNOWPLOW_API_URL"),
        api_key=get_env_var("SNOWPLOW_API_KEY"),
        api_key_id=get_env_var("SNOWPLOW_API_KEY_ID"),
        org_id=get_env_var("SNOWPLOW_ORG_ID")
    )

    # Create feature
    page_view_count = Attribute(
        name="page_view_count",
        type="int64",
        events=[Event(vendor="com.snowplowanalytics.snowplow", name="page_view", version="1-0-0")],
        aggregation="counter"
    )

    dummy_batch_source = BatchSource(
        name="dummy_batch_source",
        timestamp_field="event_time",
        database="SNOWPLOW_DEV1",
        schema="SIGNALS",
        table="SNOWPLOW_EVENTS",
        type="snowflake"
    )

    # Create view with custom entity
    test_with_user_entity = View(
        name="test_with_user_entity",
        version=3,
        entity=user_entity,
        attributes=[page_view_count],
        batch_source=dummy_batch_source
    )
    # Create view with custom entity
    test_with_session_entity = View(
        name="test_with_session_entity",
        version=3,
        entity=session_entity,
        attributes=[page_view_count],
        batch_source=dummy_batch_source
    )

    sp_signals.apply(objects=[test_with_user_entity])
    sp_signals.apply(objects=[test_with_session_entity])


    # Get view back
    retrieved_user_view = sp_signals.get_view("test_with_user_entity")
    print(f"Retrieved view: {retrieved_user_view.name}")
    print(f"Entity key: {retrieved_user_view.entity_key}")

    retrieved_session_view = sp_signals.get_view("test_with_session_entity")
    print(f"Retrieved view: {retrieved_session_view.name}")
    print(f"Entity key: {retrieved_session_view.entity_key}")

if __name__ == "__main__":
    main() 