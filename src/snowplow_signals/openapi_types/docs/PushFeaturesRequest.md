# PushFeaturesRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**push_source_name** | **str** |  | 
**df** | **Dict[str, List[object]]** |  | 
**allow_registry_cache** | **bool** |  | [optional] [default to True]
**to** | **str** |  | [optional] [default to 'online']

## Example

```python
from openapi_client.models.push_features_request import PushFeaturesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PushFeaturesRequest from a JSON string
push_features_request_instance = PushFeaturesRequest.from_json(json)
# print the JSON string representation of the object
print(PushFeaturesRequest.to_json())

# convert the object into a dict
push_features_request_dict = push_features_request_instance.to_dict()
# create an instance of PushFeaturesRequest from a dict
push_features_request_from_dict = PushFeaturesRequest.from_dict(push_features_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


