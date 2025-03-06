# FeatureRef


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of a feature in the prompt to be replaced. Will be inside double curly brackets in the prompt. | 
**reference** | **str** | The reference of the feature stored in the online store. Format is {feature_view}:{feature_name}. | 

## Example

```python
from openapi_client.models.feature_ref import FeatureRef

# TODO update the JSON string below
json = "{}"
# create an instance of FeatureRef from a JSON string
feature_ref_instance = FeatureRef.from_json(json)
# print the JSON string representation of the object
print(FeatureRef.to_json())

# convert the object into a dict
feature_ref_dict = feature_ref_instance.to_dict()
# create an instance of FeatureRef from a dict
feature_ref_from_dict = FeatureRef.from_dict(feature_ref_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


