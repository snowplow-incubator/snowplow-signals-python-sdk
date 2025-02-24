import json
from models.data_model_autogen.overview_config_generator import OverviewConfigGenerator

json_input = """{
    "name": "sample_features",
    "entities": ["{user}"],
    "online": true,
    "status": "Live",
    "description": "Example features",
    "features": [
        {
            "name": "page_view_events_count_last_7_days",
            "value_type": "INT32",
            "description": "Number of page_view events in the last 7 days",
            "scope": "lifetime",
            "events": ["iglu:com.snowplowanalytics.snowplow/web_page/jsonschema/1-0-0"],
            "type": "counter",
            "property": null,
            "filter": {
                "combinator": "and",
                "condition": [
                    {
                        "property": "event.type",
                        "operator": "equals",
                        "value": "page_view"
                    }
                ]
            },
            "signals_derived": false,
            "period": "P7D"
        }
    ],
    "fields": [
        {
            "name": "UPDATED_AT",
            "value_type": "UNIX_TIMESTAMP",
            "description": "Last updated at"
        }
    ]
}"""

# Optionally load from above json_input:
# data = json.loads(json_input)

with open("scripts/example_batch_features.json") as f:
    data = json.load(f)

generator = OverviewConfigGenerator(data=data)
output = generator.create_config_overview()

# print(json.dumps(output, indent=4))

with open("dbt_project/utils/config.json", "w") as f:
    json.dump(output, f, indent=4)

print("✅ Config file generated: config.json")
