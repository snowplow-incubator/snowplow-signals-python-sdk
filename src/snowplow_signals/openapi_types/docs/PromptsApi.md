# openapi_client.PromptsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_prompt_api_v1_prompts_post**](PromptsApi.md#create_prompt_api_v1_prompts_post) | **POST** /api/v1/prompts/ | Create Prompt
[**delete_prompt_api_v1_prompts_prompt_name_version_version_delete**](PromptsApi.md#delete_prompt_api_v1_prompts_prompt_name_version_version_delete) | **DELETE** /api/v1/prompts/{prompt_name}/version/{version} | Delete Prompt
[**get_latest_prompt_api_v1_prompts_prompt_name_get**](PromptsApi.md#get_latest_prompt_api_v1_prompts_prompt_name_get) | **GET** /api/v1/prompts/{prompt_name} | Get Latest Prompt
[**get_prompt_api_v1_prompts_prompt_name_version_version_get**](PromptsApi.md#get_prompt_api_v1_prompts_prompt_name_version_version_get) | **GET** /api/v1/prompts/{prompt_name}/version/{version} | Get Prompt
[**get_prompts_api_v1_prompts_get**](PromptsApi.md#get_prompts_api_v1_prompts_get) | **GET** /api/v1/prompts/ | Get Prompts
[**hydrate_prompt_api_v1_prompts_prompt_name_version_version_hydrate_post**](PromptsApi.md#hydrate_prompt_api_v1_prompts_prompt_name_version_version_hydrate_post) | **POST** /api/v1/prompts/{prompt_name}/version/{version}/hydrate | Hydrate Prompt


# **create_prompt_api_v1_prompts_post**
> PromptResponse create_prompt_api_v1_prompts_post(prompt_base)

Create Prompt

### Example


```python
import openapi_client
from openapi_client.models.prompt_base import PromptBase
from openapi_client.models.prompt_response import PromptResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.PromptsApi(api_client)
    prompt_base = openapi_client.PromptBase() # PromptBase | 

    try:
        # Create Prompt
        api_response = api_instance.create_prompt_api_v1_prompts_post(prompt_base)
        print("The response of PromptsApi->create_prompt_api_v1_prompts_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PromptsApi->create_prompt_api_v1_prompts_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **prompt_base** | [**PromptBase**](PromptBase.md)|  | 

### Return type

[**PromptResponse**](PromptResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_prompt_api_v1_prompts_prompt_name_version_version_delete**
> PromptDeletedResponse delete_prompt_api_v1_prompts_prompt_name_version_version_delete(prompt_name, version)

Delete Prompt

### Example


```python
import openapi_client
from openapi_client.models.prompt_deleted_response import PromptDeletedResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.PromptsApi(api_client)
    prompt_name = 'prompt_name_example' # str | 
    version = 56 # int | 

    try:
        # Delete Prompt
        api_response = api_instance.delete_prompt_api_v1_prompts_prompt_name_version_version_delete(prompt_name, version)
        print("The response of PromptsApi->delete_prompt_api_v1_prompts_prompt_name_version_version_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PromptsApi->delete_prompt_api_v1_prompts_prompt_name_version_version_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **prompt_name** | **str**|  | 
 **version** | **int**|  | 

### Return type

[**PromptDeletedResponse**](PromptDeletedResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_latest_prompt_api_v1_prompts_prompt_name_get**
> PromptResponse get_latest_prompt_api_v1_prompts_prompt_name_get(prompt_name, version=version)

Get Latest Prompt

### Example


```python
import openapi_client
from openapi_client.models.prompt_response import PromptResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.PromptsApi(api_client)
    prompt_name = 'prompt_name_example' # str | 
    version = 56 # int |  (optional)

    try:
        # Get Latest Prompt
        api_response = api_instance.get_latest_prompt_api_v1_prompts_prompt_name_get(prompt_name, version=version)
        print("The response of PromptsApi->get_latest_prompt_api_v1_prompts_prompt_name_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PromptsApi->get_latest_prompt_api_v1_prompts_prompt_name_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **prompt_name** | **str**|  | 
 **version** | **int**|  | [optional] 

### Return type

[**PromptResponse**](PromptResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_prompt_api_v1_prompts_prompt_name_version_version_get**
> PromptResponse get_prompt_api_v1_prompts_prompt_name_version_version_get(prompt_name, version)

Get Prompt

### Example


```python
import openapi_client
from openapi_client.models.prompt_response import PromptResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.PromptsApi(api_client)
    prompt_name = 'prompt_name_example' # str | 
    version = 56 # int | 

    try:
        # Get Prompt
        api_response = api_instance.get_prompt_api_v1_prompts_prompt_name_version_version_get(prompt_name, version)
        print("The response of PromptsApi->get_prompt_api_v1_prompts_prompt_name_version_version_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PromptsApi->get_prompt_api_v1_prompts_prompt_name_version_version_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **prompt_name** | **str**|  | 
 **version** | **int**|  | 

### Return type

[**PromptResponse**](PromptResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_prompts_api_v1_prompts_get**
> List[PromptResponse] get_prompts_api_v1_prompts_get()

Get Prompts

### Example


```python
import openapi_client
from openapi_client.models.prompt_response import PromptResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.PromptsApi(api_client)

    try:
        # Get Prompts
        api_response = api_instance.get_prompts_api_v1_prompts_get()
        print("The response of PromptsApi->get_prompts_api_v1_prompts_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PromptsApi->get_prompts_api_v1_prompts_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[PromptResponse]**](PromptResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **hydrate_prompt_api_v1_prompts_prompt_name_version_version_hydrate_post**
> object hydrate_prompt_api_v1_prompts_prompt_name_version_version_hydrate_post(prompt_name, version, entity_identifiers)

Hydrate Prompt

### Example


```python
import openapi_client
from openapi_client.models.entity_identifiers import EntityIdentifiers
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.PromptsApi(api_client)
    prompt_name = 'prompt_name_example' # str | 
    version = 56 # int | 
    entity_identifiers = openapi_client.EntityIdentifiers() # EntityIdentifiers | 

    try:
        # Hydrate Prompt
        api_response = api_instance.hydrate_prompt_api_v1_prompts_prompt_name_version_version_hydrate_post(prompt_name, version, entity_identifiers)
        print("The response of PromptsApi->hydrate_prompt_api_v1_prompts_prompt_name_version_version_hydrate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PromptsApi->hydrate_prompt_api_v1_prompts_prompt_name_version_version_hydrate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **prompt_name** | **str**|  | 
 **version** | **int**|  | 
 **entity_identifiers** | [**EntityIdentifiers**](EntityIdentifiers.md)|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

