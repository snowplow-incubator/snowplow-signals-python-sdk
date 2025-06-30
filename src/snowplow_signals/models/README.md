# Generating the models from the API spec

1. Download the `openapi.json` definition file from `http://localhost:8000/openapi.json`
2. Run the following script to generate the model file:

```sh
poetry run datamodel-codegen --input openapi.json --output model.py --output-model-type pydantic_v2.BaseModel --enum-field-as-literal all --use-default-kwarg
```

3. Replace the `model.py` file in this folder.
