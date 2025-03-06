# Entity

Defines entities for which features can be defined. An entity can also contain associated metadata.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The unique name of the object. | 
**description** | **str** |  | [optional] 
**join_keys** | **List[str]** |  | [optional] 
**value_type** | **str** | The type of the entity, such as string or float. | [optional] [default to 'UNKNOWN']
**tags** | **Dict[str, str]** |  | [optional] 
**owner** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.entity import Entity

# TODO update the JSON string below
json = "{}"
# create an instance of Entity from a JSON string
entity_instance = Entity.from_json(json)
# print the JSON string representation of the object
print(Entity.to_json())

# convert the object into a dict
entity_dict = entity_instance.to_dict()
# create an instance of Entity from a dict
entity_from_dict = Entity.from_dict(entity_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


