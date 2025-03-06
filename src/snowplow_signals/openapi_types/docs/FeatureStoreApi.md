# openapi_client.FeatureStoreApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**apply_to_feast_api_v1_feature_store_apply_post**](FeatureStoreApi.md#apply_to_feast_api_v1_feature_store_apply_post) | **POST** /api/v1/feature_store/apply | Apply To Feast
[**get_feast_data_sources_api_v1_feature_store_data_sources_get**](FeatureStoreApi.md#get_feast_data_sources_api_v1_feature_store_data_sources_get) | **GET** /api/v1/feature_store/data_sources | Get Feast Data Sources
[**get_feast_feature_services_api_v1_feature_store_feature_services_get**](FeatureStoreApi.md#get_feast_feature_services_api_v1_feature_store_feature_services_get) | **GET** /api/v1/feature_store/feature_services | Get Feast Feature Services
[**get_feast_feature_views_api_v1_feature_store_feature_views_get**](FeatureStoreApi.md#get_feast_feature_views_api_v1_feature_store_feature_views_get) | **GET** /api/v1/feature_store/feature_views | Get Feast Feature Views


# **apply_to_feast_api_v1_feature_store_apply_post**
> Dict[str, str] apply_to_feast_api_v1_feature_store_apply_post()

Apply To Feast

### Example


```python
import openapi_client
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
    api_instance = openapi_client.FeatureStoreApi(api_client)

    try:
        # Apply To Feast
        api_response = api_instance.apply_to_feast_api_v1_feature_store_apply_post()
        print("The response of FeatureStoreApi->apply_to_feast_api_v1_feature_store_apply_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FeatureStoreApi->apply_to_feast_api_v1_feature_store_apply_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**Dict[str, str]**

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

# **get_feast_data_sources_api_v1_feature_store_data_sources_get**
> object get_feast_data_sources_api_v1_feature_store_data_sources_get()

Get Feast Data Sources

### Example


```python
import openapi_client
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
    api_instance = openapi_client.FeatureStoreApi(api_client)

    try:
        # Get Feast Data Sources
        api_response = api_instance.get_feast_data_sources_api_v1_feature_store_data_sources_get()
        print("The response of FeatureStoreApi->get_feast_data_sources_api_v1_feature_store_data_sources_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FeatureStoreApi->get_feast_data_sources_api_v1_feature_store_data_sources_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

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

# **get_feast_feature_services_api_v1_feature_store_feature_services_get**
> object get_feast_feature_services_api_v1_feature_store_feature_services_get()

Get Feast Feature Services

### Example


```python
import openapi_client
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
    api_instance = openapi_client.FeatureStoreApi(api_client)

    try:
        # Get Feast Feature Services
        api_response = api_instance.get_feast_feature_services_api_v1_feature_store_feature_services_get()
        print("The response of FeatureStoreApi->get_feast_feature_services_api_v1_feature_store_feature_services_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FeatureStoreApi->get_feast_feature_services_api_v1_feature_store_feature_services_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

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

# **get_feast_feature_views_api_v1_feature_store_feature_views_get**
> object get_feast_feature_views_api_v1_feature_store_feature_views_get()

Get Feast Feature Views

### Example


```python
import openapi_client
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
    api_instance = openapi_client.FeatureStoreApi(api_client)

    try:
        # Get Feast Feature Views
        api_response = api_instance.get_feast_feature_views_api_v1_feature_store_feature_views_get()
        print("The response of FeatureStoreApi->get_feast_feature_views_api_v1_feature_store_feature_views_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FeatureStoreApi->get_feast_feature_views_api_v1_feature_store_feature_views_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

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

