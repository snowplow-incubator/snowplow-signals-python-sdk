# FeatureViewInput

A FeatureView defines a logical group of features.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The unique name of the feature view. | 
**version** | **int** | The version of the feature view. | [optional] [default to 1]
**entities** | [**List[EntityLink]**](EntityLink.md) | The list of names of entities that this feature view is associated with. | [optional] 
**ttl** | **str** |  | [optional] 
**source** | [**DataSourceLink**](DataSourceLink.md) |  | [optional] 
**online** | **bool** | A boolean indicating whether online retrieval is enabled for this feature view. | [optional] [default to True]
**description** | **str** |  | [optional] 
**tags** | **Dict[str, str]** |  | [optional] 
**owner** | **str** |  | [optional] 
**fields** | [**List[ModelField]**](ModelField.md) | The schema of the feature view, including timestamp, and entity columns. If not specified, can be inferred from the underlying data source. | [optional] 
**features** | [**List[FeatureInput]**](FeatureInput.md) | The list of features that are part of this feature view. | [optional] 
**status** | **str** | The status of the feature view. | [optional] [default to 'Draft']

## Example

```python
from openapi_client.models.feature_view_input import FeatureViewInput

# TODO update the JSON string below
json = "{}"
# create an instance of FeatureViewInput from a JSON string
feature_view_input_instance = FeatureViewInput.from_json(json)
# print the JSON string representation of the object
print(FeatureViewInput.to_json())

# convert the object into a dict
feature_view_input_dict = feature_view_input_instance.to_dict()
# create an instance of FeatureViewInput from a dict
feature_view_input_from_dict = FeatureViewInput.from_dict(feature_view_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


