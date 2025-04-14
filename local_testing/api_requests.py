import os
from snowplow_signals.api_client import ApiClient

def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Environment variable {name} is not set")
    return value

def main():
    # Initialize API client
    api_client = ApiClient(
        api_url=get_env_var("SNOWPLOW_API_URL"),
        api_key=get_env_var("SNOWPLOW_API_KEY"),
        api_key_id=get_env_var("SNOWPLOW_API_KEY_ID"),
        org_id=get_env_var("SNOWPLOW_ORG_ID")
    )

    try:
        # Get all views
        print("\nGetting all views...")
        views = api_client.make_request(
            method="GET",
            endpoint="registry/views/",
            params={"offline": True}
        )
        print(f"Found {len(views)} views")
        for view in views:
            print(f"\nView: {view['name']} (v{view['version']})")
            print(f"Entity: {view['entity']['name']}")
            print(f"Entity Key: {view.get('entity_key', 'Not specified')}")
            print(f"Offline: {view.get('offline', False)}")
        # Get all entities
        print("\nGetting all entities...")
        entities = api_client.make_request(
            method="GET",
            endpoint="feature_store/entities"
        )
        print(f"Found {len(entities)} entities")
        for entity in entities:
            print(f"\nEntity: {entity['name']}")
            print(f"Key: {entity.get('key', 'Not specified')}")

        # Get all feature views
        print("\nGetting all feature views...")
        feature_views = api_client.make_request(
            method="GET",
            endpoint="feature_store/feature_views"
        )
        print(f"Found {len(feature_views)} feature views")
        for fv in feature_views:
            print(f"\nFeature View: {fv['name']}")
            print(f"Entity: {fv.get('entity_name', 'Not specified')}")

        # Get all data sources
        print("\nGetting all data sources...")
        data_sources = api_client.make_request(
            method="GET",
            endpoint="feature_store/data_sources"
        )
        print(f"Found {len(data_sources)} data sources")
        for ds in data_sources:
            print(f"\nData Source: {ds['name']}")
            print(f"Type: {ds.get('type', 'Not specified')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 