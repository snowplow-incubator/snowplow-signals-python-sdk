# FilterCombinator


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**combinator** | **str** | The logical operator used to combine the conditions. | 
**condition** | [**List[FilterCondition]**](FilterCondition.md) | An array of conditions used to filter the events. | 

## Example

```python
from openapi_client.models.filter_combinator import FilterCombinator

# TODO update the JSON string below
json = "{}"
# create an instance of FilterCombinator from a JSON string
filter_combinator_instance = FilterCombinator.from_json(json)
# print the JSON string representation of the object
print(FilterCombinator.to_json())

# convert the object into a dict
filter_combinator_dict = filter_combinator_instance.to_dict()
# create an instance of FilterCombinator from a dict
filter_combinator_from_dict = FilterCombinator.from_dict(filter_combinator_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


