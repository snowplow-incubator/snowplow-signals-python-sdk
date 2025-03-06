# openapi_client.FeaturesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_online_features_api_v1_get_online_features_post**](FeaturesApi.md#get_online_features_api_v1_get_online_features_post) | **POST** /api/v1/get-online-features | Get Online Features
[**push_api_v1_push_post**](FeaturesApi.md#push_api_v1_push_post) | **POST** /api/v1/push | Push


# **get_online_features_api_v1_get_online_features_post**
> Dict[str, List[object]] get_online_features_api_v1_get_online_features_post(get_online_features_request)

Get Online Features

### Example


```python
import openapi_client
from openapi_client.models.get_online_features_request import GetOnlineFeaturesRequest
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
    api_instance = openapi_client.FeaturesApi(api_client)
    get_online_features_request = openapi_client.GetOnlineFeaturesRequest() # GetOnlineFeaturesRequest | 

    try:
        # Get Online Features
        api_response = api_instance.get_online_features_api_v1_get_online_features_post(get_online_features_request)
        print("The response of FeaturesApi->get_online_features_api_v1_get_online_features_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FeaturesApi->get_online_features_api_v1_get_online_features_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **get_online_features_request** | [**GetOnlineFeaturesRequest**](GetOnlineFeaturesRequest.md)|  | 

### Return type

**Dict[str, List[object]]**

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

# **push_api_v1_push_post**
> object push_api_v1_push_post(push_features_request)

Push

### Example


```python
import openapi_client
from openapi_client.models.push_features_request import PushFeaturesRequest
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
    api_instance = openapi_client.FeaturesApi(api_client)
    push_features_request = openapi_client.PushFeaturesRequest() # PushFeaturesRequest | 

    try:
        # Push
        api_response = api_instance.push_api_v1_push_post(push_features_request)
        print("The response of FeaturesApi->push_api_v1_push_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FeaturesApi->push_api_v1_push_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **push_features_request** | [**PushFeaturesRequest**](PushFeaturesRequest.md)|  | 

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

