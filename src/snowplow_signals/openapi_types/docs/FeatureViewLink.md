# FeatureViewLink

A FeatureView defines a logical group of features.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version** | **int** | The version of the feature view. | [optional] [default to 1]
**name** | **str** | The unique name of the feature view. | 

## Example

```python
from openapi_client.models.feature_view_link import FeatureViewLink

# TODO update the JSON string below
json = "{}"
# create an instance of FeatureViewLink from a JSON string
feature_view_link_instance = FeatureViewLink.from_json(json)
# print the JSON string representation of the object
print(FeatureViewLink.to_json())

# convert the object into a dict
feature_view_link_dict = feature_view_link_instance.to_dict()
# create an instance of FeatureViewLink from a dict
feature_view_link_from_dict = FeatureViewLink.from_dict(feature_view_link_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


