# FeatureOutput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the field. | 
**description** | **str** |  | [optional] 
**dtype** | **str** | The type of the field, such as string or float. | [optional] [default to 'UNKNOWN']
**tags** | **Dict[str, str]** |  | [optional] 
**vector_index** | **bool** | If set to True the field will be indexed for vector similarity search. | [optional] [default to False]
**vector_search_metric** | **str** |  | [optional] 
**scope** | **str** | The scope of the feature, either session or lifetime. | 
**events** | **List[str]** | An array of events used to calculate this trait. | 
**type** | **str** | The calculation type of the feature. | 
**var_property** | **str** |  | [optional] 
**filter** | [**FilterCombinator**](FilterCombinator.md) |  | [optional] 
**signals_derived** | **bool** | Determines if the trait should be inferred from signals | [optional] [default to False]

## Example

```python
from openapi_client.models.feature_output import FeatureOutput

# TODO update the JSON string below
json = "{}"
# create an instance of FeatureOutput from a JSON string
feature_output_instance = FeatureOutput.from_json(json)
# print the JSON string representation of the object
print(FeatureOutput.to_json())

# convert the object into a dict
feature_output_dict = feature_output_instance.to_dict()
# create an instance of FeatureOutput from a dict
feature_output_from_dict = FeatureOutput.from_dict(feature_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


