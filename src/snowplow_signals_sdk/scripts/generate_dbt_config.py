import json
from models.data_model_autogen.dbt_config_generator import DbtConfigGenerator


with open("dbt_project/utils/config.json") as f:
    data = json.load(f)

generator = DbtConfigGenerator(data=data)
output = generator.create_dbt_config()

# print(json.dumps(output, indent=4))

with open("dbt_project/utils/dbt_config.json", "w") as f:
    json.dump(output, f, indent=4)

print("✅ Dbt Config file generated: dbt_config.json")
