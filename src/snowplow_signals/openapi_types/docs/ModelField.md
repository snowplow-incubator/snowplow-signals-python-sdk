# ModelField

A Field represents a set of values with the same structure.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the field. | 
**description** | **str** |  | [optional] 
**dtype** | **str** | The type of the field, such as string or float. | [optional] [default to 'UNKNOWN']
**tags** | **Dict[str, str]** |  | [optional] 
**vector_index** | **bool** | If set to True the field will be indexed for vector similarity search. | [optional] [default to False]
**vector_search_metric** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.model_field import ModelField

# TODO update the JSON string below
json = "{}"
# create an instance of ModelField from a JSON string
model_field_instance = ModelField.from_json(json)
# print the JSON string representation of the object
print(ModelField.to_json())

# convert the object into a dict
model_field_dict = model_field_instance.to_dict()
# create an instance of ModelField from a dict
model_field_from_dict = ModelField.from_dict(model_field_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


