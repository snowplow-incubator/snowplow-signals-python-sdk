# FilterCondition


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_property** | **str** | The path to the property on the event or entity you wish to filter. | 
**operator** | **str** | The operator used to compare the property to the value. | 
**value** | [**Value**](Value.md) |  | 

## Example

```python
from openapi_client.models.filter_condition import FilterCondition

# TODO update the JSON string below
json = "{}"
# create an instance of FilterCondition from a JSON string
filter_condition_instance = FilterCondition.from_json(json)
# print the JSON string representation of the object
print(FilterCondition.to_json())

# convert the object into a dict
filter_condition_dict = filter_condition_instance.to_dict()
# create an instance of FilterCondition from a dict
filter_condition_from_dict = FilterCondition.from_dict(filter_condition_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


