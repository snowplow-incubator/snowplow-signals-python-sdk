# GetOnlineFeaturesRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entities** | **Dict[str, List[object]]** |  | 
**feature_service** | **str** |  | [optional] 
**features** | **List[str]** |  | [optional] 
**full_feature_names** | **bool** |  | [optional] [default to False]

## Example

```python
from openapi_client.models.get_online_features_request import GetOnlineFeaturesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of GetOnlineFeaturesRequest from a JSON string
get_online_features_request_instance = GetOnlineFeaturesRequest.from_json(json)
# print the JSON string representation of the object
print(GetOnlineFeaturesRequest.to_json())

# convert the object into a dict
get_online_features_request_dict = get_online_features_request_instance.to_dict()
# create an instance of GetOnlineFeaturesRequest from a dict
get_online_features_request_from_dict = GetOnlineFeaturesRequest.from_dict(get_online_features_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


