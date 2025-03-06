# FeatureService

A feature service defines a logical group of features from one or more feature views. This group of features can be retrieved together during training or serving.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The unique name of the object. | 
**description** | **str** |  | [optional] 
**feature_views** | [**List[FeatureViewLink]**](FeatureViewLink.md) | A list containing feature views and feature view projections, representing the features in the feature service. | [optional] [default to []]
**tags** | **Dict[str, str]** |  | [optional] 
**owner** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.feature_service import FeatureService

# TODO update the JSON string below
json = "{}"
# create an instance of FeatureService from a JSON string
feature_service_instance = FeatureService.from_json(json)
# print the JSON string representation of the object
print(FeatureService.to_json())

# convert the object into a dict
feature_service_dict = feature_service_instance.to_dict()
# create an instance of FeatureService from a dict
feature_service_from_dict = FeatureService.from_dict(feature_service_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


