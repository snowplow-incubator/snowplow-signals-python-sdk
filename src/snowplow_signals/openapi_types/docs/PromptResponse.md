# PromptResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the prompt, given by the user. Also used by the SDK as reference to fetch a prompt. | 
**version** | **int** | The version of the prompt, incremented automatically when updating the prompt. | 
**prompt** | **str** | The contents of the prompt, written by the user. | 
**features** | [**List[FeatureRef]**](FeatureRef.md) | The features the prompt references by name. | 
**labels** | **List[str]** | A list of labels that are only added by the system. E.g. &#39;production&#39;, &#39;latest&#39; | 
**tags** | **List[str]** | A list of tags to categorize the prompt. | 
**author** | **str** | The author of the prompt. | 
**commit_msg** | **str** |  | 
**id** | **str** |  | 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 

## Example

```python
from openapi_client.models.prompt_response import PromptResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PromptResponse from a JSON string
prompt_response_instance = PromptResponse.from_json(json)
# print the JSON string representation of the object
print(PromptResponse.to_json())

# convert the object into a dict
prompt_response_dict = prompt_response_instance.to_dict()
# create an instance of PromptResponse from a dict
prompt_response_from_dict = PromptResponse.from_dict(prompt_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


