# openapi_client.RegistryApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_data_source_api_v1_registry_data_sources_post**](RegistryApi.md#create_data_source_api_v1_registry_data_sources_post) | **POST** /api/v1/registry/data_sources/ | Create Data Source
[**create_entity_api_v1_registry_entities_post**](RegistryApi.md#create_entity_api_v1_registry_entities_post) | **POST** /api/v1/registry/entities/ | Create Entity
[**create_feature_service_api_v1_registry_feature_services_post**](RegistryApi.md#create_feature_service_api_v1_registry_feature_services_post) | **POST** /api/v1/registry/feature_services/ | Create Feature Service
[**create_feature_view_api_v1_registry_feature_views_post**](RegistryApi.md#create_feature_view_api_v1_registry_feature_views_post) | **POST** /api/v1/registry/feature_views/ | Create Feature View
[**delete_data_source_api_v1_registry_data_sources_data_source_name_delete**](RegistryApi.md#delete_data_source_api_v1_registry_data_sources_data_source_name_delete) | **DELETE** /api/v1/registry/data_sources/{data_source_name} | Delete Data Source
[**delete_entity_api_v1_registry_entities_entity_name_delete**](RegistryApi.md#delete_entity_api_v1_registry_entities_entity_name_delete) | **DELETE** /api/v1/registry/entities/{entity_name} | Delete Entity
[**delete_feature_service_api_v1_registry_feature_services_feature_service_name_delete**](RegistryApi.md#delete_feature_service_api_v1_registry_feature_services_feature_service_name_delete) | **DELETE** /api/v1/registry/feature_services/{feature_service_name} | Delete Feature Service
[**delete_feature_view_api_v1_registry_feature_views_feature_view_name_versions_version_delete**](RegistryApi.md#delete_feature_view_api_v1_registry_feature_views_feature_view_name_versions_version_delete) | **DELETE** /api/v1/registry/feature_views/{feature_view_name}/versions/{version} | Delete Feature View
[**get_all_data_sources_api_v1_registry_data_sources_get**](RegistryApi.md#get_all_data_sources_api_v1_registry_data_sources_get) | **GET** /api/v1/registry/data_sources/ | Get All Data Sources
[**get_all_entities_api_v1_registry_entities_get**](RegistryApi.md#get_all_entities_api_v1_registry_entities_get) | **GET** /api/v1/registry/entities/ | Get All Entities
[**get_all_feature_services_api_v1_registry_feature_services_get**](RegistryApi.md#get_all_feature_services_api_v1_registry_feature_services_get) | **GET** /api/v1/registry/feature_services/ | Get All Feature Services
[**get_all_feature_views_api_v1_registry_feature_views_get**](RegistryApi.md#get_all_feature_views_api_v1_registry_feature_views_get) | **GET** /api/v1/registry/feature_views/ | Get All Feature Views
[**get_data_source_api_v1_registry_data_sources_data_source_name_get**](RegistryApi.md#get_data_source_api_v1_registry_data_sources_data_source_name_get) | **GET** /api/v1/registry/data_sources/{data_source_name} | Get Data Source
[**get_entity_api_v1_registry_entities_entity_name_get**](RegistryApi.md#get_entity_api_v1_registry_entities_entity_name_get) | **GET** /api/v1/registry/entities/{entity_name} | Get Entity
[**get_feature_service_api_v1_registry_feature_services_feature_service_name_get**](RegistryApi.md#get_feature_service_api_v1_registry_feature_services_feature_service_name_get) | **GET** /api/v1/registry/feature_services/{feature_service_name} | Get Feature Service
[**get_feature_view_with_version_api_v1_registry_feature_views_feature_view_name_versions_version_get**](RegistryApi.md#get_feature_view_with_version_api_v1_registry_feature_views_feature_view_name_versions_version_get) | **GET** /api/v1/registry/feature_views/{feature_view_name}/versions/{version} | Get Feature View With Version
[**get_latest_feature_view_api_v1_registry_feature_views_feature_view_name_get**](RegistryApi.md#get_latest_feature_view_api_v1_registry_feature_views_feature_view_name_get) | **GET** /api/v1/registry/feature_views/{feature_view_name} | Get Latest Feature View


# **create_data_source_api_v1_registry_data_sources_post**
> DataSource create_data_source_api_v1_registry_data_sources_post(data_source)

Create Data Source

### Example


```python
import openapi_client
from openapi_client.models.data_source import DataSource
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
    api_instance = openapi_client.RegistryApi(api_client)
    data_source = openapi_client.DataSource() # DataSource | 

    try:
        # Create Data Source
        api_response = api_instance.create_data_source_api_v1_registry_data_sources_post(data_source)
        print("The response of RegistryApi->create_data_source_api_v1_registry_data_sources_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RegistryApi->create_data_source_api_v1_registry_data_sources_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **data_source** | [**DataSource**](DataSource.md)|  | 

### Return type

[**DataSource**](DataSource.md)

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

# **create_entity_api_v1_registry_entities_post**
> Entity create_entity_api_v1_registry_entities_post(entity)

Create Entity

### Example


```python
import openapi_client
from openapi_client.models.entity import Entity
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
    api_instance = openapi_client.RegistryApi(api_client)
    entity = openapi_client.Entity() # Entity | 

    try:
        # Create Entity
        api_response = api_instance.create_entity_api_v1_registry_entities_post(entity)
        print("The response of RegistryApi->create_entity_api_v1_registry_entities_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RegistryApi->create_entity_api_v1_registry_entities_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity** | [**Entity**](Entity.md)|  | 

### Return type

[**Entity**](Entity.md)

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

# **create_feature_service_api_v1_registry_feature_services_post**
> FeatureService create_feature_service_api_v1_registry_feature_services_post(feature_service)

Create Feature Service

### Example


```python
import openapi_client
from openapi_client.models.feature_service import FeatureService
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
    api_instance = openapi_client.RegistryApi(api_client)
    feature_service = openapi_client.FeatureService() # FeatureService | 

    try:
        # Create Feature Service
        api_response = api_instance.create_feature_service_api_v1_registry_feature_services_post(feature_service)
        print("The response of RegistryApi->create_feature_service_api_v1_registry_feature_services_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RegistryApi->create_feature_service_api_v1_registry_feature_services_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **feature_service** | [**FeatureService**](FeatureService.md)|  | 

### Return type

[**FeatureService**](FeatureService.md)

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

# **create_feature_view_api_v1_registry_feature_views_post**
> FeatureViewOutput create_feature_view_api_v1_registry_feature_views_post(feature_view_input)

Create Feature View

### Example


```python
import openapi_client
from openapi_client.models.feature_view_input import FeatureViewInput
from openapi_client.models.feature_view_output import FeatureViewOutput
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
    api_instance = openapi_client.RegistryApi(api_client)
    feature_view_input = openapi_client.FeatureViewInput() # FeatureViewInput | 

    try:
        # Create Feature View
        api_response = api_instance.create_feature_view_api_v1_registry_feature_views_post(feature_view_input)
        print("The response of RegistryApi->create_feature_view_api_v1_registry_feature_views_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RegistryApi->create_feature_view_api_v1_registry_feature_views_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **feature_view_input** | [**FeatureViewInput**](FeatureViewInput.md)|  | 

### Return type

[**FeatureViewOutput**](FeatureViewOutput.md)

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

# **delete_data_source_api_v1_registry_data_sources_data_source_name_delete**
> object delete_data_source_api_v1_registry_data_sources_data_source_name_delete(data_source_name)

Delete Data Source

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
    api_instance = openapi_client.RegistryApi(api_client)
    data_source_name = 'data_source_name_example' # str | 

    try:
        # Delete Data Source
        api_response = api_instance.delete_data_source_api_v1_registry_data_sources_data_source_name_delete(data_source_name)
        print("The response of RegistryApi->delete_data_source_api_v1_registry_data_sources_data_source_name_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RegistryApi->delete_data_source_api_v1_registry_data_sources_data_source_name_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **data_source_name** | **str**|  | 

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_entity_api_v1_registry_entities_entity_name_delete**
> object delete_entity_api_v1_registry_entities_entity_name_delete(entity_name)

Delete Entity

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
    api_instance = openapi_client.RegistryApi(api_client)
    entity_name = 'entity_name_example' # str | 

    try:
        # Delete Entity
        api_response = api_instance.delete_entity_api_v1_registry_entities_entity_name_delete(entity_name)
        print("The response of RegistryApi->delete_entity_api_v1_registry_entities_entity_name_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RegistryApi->delete_entity_api_v1_registry_entities_entity_name_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_name** | **str**|  | 

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_feature_service_api_v1_registry_feature_services_feature_service_name_delete**
> object delete_feature_service_api_v1_registry_feature_services_feature_service_name_delete(feature_service_name)

Delete Feature Service

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
    api_instance = openapi_client.RegistryApi(api_client)
    feature_service_name = 'feature_service_name_example' # str | 

    try:
        # Delete Feature Service
        api_response = api_instance.delete_feature_service_api_v1_registry_feature_services_feature_service_name_delete(feature_service_name)
        print("The response of RegistryApi->delete_feature_service_api_v1_registry_feature_services_feature_service_name_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RegistryApi->delete_feature_service_api_v1_registry_feature_services_feature_service_name_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **feature_service_name** | **str**|  | 

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_feature_view_api_v1_registry_feature_views_feature_view_name_versions_version_delete**
> object delete_feature_view_api_v1_registry_feature_views_feature_view_name_versions_version_delete(feature_view_name, version)

Delete Feature View

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
    api_instance = openapi_client.RegistryApi(api_client)
    feature_view_name = 'feature_view_name_example' # str | 
    version = 56 # int | 

    try:
        # Delete Feature View
        api_response = api_instance.delete_feature_view_api_v1_registry_feature_views_feature_view_name_versions_version_delete(feature_view_name, version)
        print("The response of RegistryApi->delete_feature_view_api_v1_registry_feature_views_feature_view_name_versions_version_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RegistryApi->delete_feature_view_api_v1_registry_feature_views_feature_view_name_versions_version_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **feature_view_name** | **str**|  | 
 **version** | **int**|  | 

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_data_sources_api_v1_registry_data_sources_get**
> List[DataSource] get_all_data_sources_api_v1_registry_data_sources_get()

Get All Data Sources

### Example


```python
import openapi_client
from openapi_client.models.data_source import DataSource
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
    api_instance = openapi_client.RegistryApi(api_client)

    try:
        # Get All Data Sources
        api_response = api_instance.get_all_data_sources_api_v1_registry_data_sources_get()
        print("The response of RegistryApi->get_all_data_sources_api_v1_registry_data_sources_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RegistryApi->get_all_data_sources_api_v1_registry_data_sources_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[DataSource]**](DataSource.md)

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

# **get_all_entities_api_v1_registry_entities_get**
> List[Entity] get_all_entities_api_v1_registry_entities_get()

Get All Entities

### Example


```python
import openapi_client
from openapi_client.models.entity import Entity
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
    api_instance = openapi_client.RegistryApi(api_client)

    try:
        # Get All Entities
        api_response = api_instance.get_all_entities_api_v1_registry_entities_get()
        print("The response of RegistryApi->get_all_entities_api_v1_registry_entities_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RegistryApi->get_all_entities_api_v1_registry_entities_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[Entity]**](Entity.md)

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

# **get_all_feature_services_api_v1_registry_feature_services_get**
> List[FeatureService] get_all_feature_services_api_v1_registry_feature_services_get()

Get All Feature Services

### Example


```python
import openapi_client
from openapi_client.models.feature_service import FeatureService
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
    api_instance = openapi_client.RegistryApi(api_client)

    try:
        # Get All Feature Services
        api_response = api_instance.get_all_feature_services_api_v1_registry_feature_services_get()
        print("The response of RegistryApi->get_all_feature_services_api_v1_registry_feature_services_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RegistryApi->get_all_feature_services_api_v1_registry_feature_services_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[FeatureService]**](FeatureService.md)

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

# **get_all_feature_views_api_v1_registry_feature_views_get**
> List[FeatureViewOutput] get_all_feature_views_api_v1_registry_feature_views_get(source_type=source_type, status=status, applied=applied)

Get All Feature Views

### Example


```python
import openapi_client
from openapi_client.models.feature_view_output import FeatureViewOutput
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
    api_instance = openapi_client.RegistryApi(api_client)
    source_type = 'source_type_example' # str |  (optional)
    status = 'status_example' # str |  (optional)
    applied = True # bool |  (optional)

    try:
        # Get All Feature Views
        api_response = api_instance.get_all_feature_views_api_v1_registry_feature_views_get(source_type=source_type, status=status, applied=applied)
        print("The response of RegistryApi->get_all_feature_views_api_v1_registry_feature_views_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RegistryApi->get_all_feature_views_api_v1_registry_feature_views_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_type** | **str**|  | [optional] 
 **status** | **str**|  | [optional] 
 **applied** | **bool**|  | [optional] 

### Return type

[**List[FeatureViewOutput]**](FeatureViewOutput.md)

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

# **get_data_source_api_v1_registry_data_sources_data_source_name_get**
> DataSource get_data_source_api_v1_registry_data_sources_data_source_name_get(data_source_name)

Get Data Source

### Example


```python
import openapi_client
from openapi_client.models.data_source import DataSource
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
    api_instance = openapi_client.RegistryApi(api_client)
    data_source_name = 'data_source_name_example' # str | 

    try:
        # Get Data Source
        api_response = api_instance.get_data_source_api_v1_registry_data_sources_data_source_name_get(data_source_name)
        print("The response of RegistryApi->get_data_source_api_v1_registry_data_sources_data_source_name_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RegistryApi->get_data_source_api_v1_registry_data_sources_data_source_name_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **data_source_name** | **str**|  | 

### Return type

[**DataSource**](DataSource.md)

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

# **get_entity_api_v1_registry_entities_entity_name_get**
> Entity get_entity_api_v1_registry_entities_entity_name_get(entity_name)

Get Entity

### Example


```python
import openapi_client
from openapi_client.models.entity import Entity
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
    api_instance = openapi_client.RegistryApi(api_client)
    entity_name = 'entity_name_example' # str | 

    try:
        # Get Entity
        api_response = api_instance.get_entity_api_v1_registry_entities_entity_name_get(entity_name)
        print("The response of RegistryApi->get_entity_api_v1_registry_entities_entity_name_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RegistryApi->get_entity_api_v1_registry_entities_entity_name_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_name** | **str**|  | 

### Return type

[**Entity**](Entity.md)

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

# **get_feature_service_api_v1_registry_feature_services_feature_service_name_get**
> FeatureService get_feature_service_api_v1_registry_feature_services_feature_service_name_get(feature_service_name)

Get Feature Service

### Example


```python
import openapi_client
from openapi_client.models.feature_service import FeatureService
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
    api_instance = openapi_client.RegistryApi(api_client)
    feature_service_name = 'feature_service_name_example' # str | 

    try:
        # Get Feature Service
        api_response = api_instance.get_feature_service_api_v1_registry_feature_services_feature_service_name_get(feature_service_name)
        print("The response of RegistryApi->get_feature_service_api_v1_registry_feature_services_feature_service_name_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RegistryApi->get_feature_service_api_v1_registry_feature_services_feature_service_name_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **feature_service_name** | **str**|  | 

### Return type

[**FeatureService**](FeatureService.md)

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

# **get_feature_view_with_version_api_v1_registry_feature_views_feature_view_name_versions_version_get**
> FeatureViewOutput get_feature_view_with_version_api_v1_registry_feature_views_feature_view_name_versions_version_get(feature_view_name, version)

Get Feature View With Version

### Example


```python
import openapi_client
from openapi_client.models.feature_view_output import FeatureViewOutput
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
    api_instance = openapi_client.RegistryApi(api_client)
    feature_view_name = 'feature_view_name_example' # str | 
    version = 56 # int | 

    try:
        # Get Feature View With Version
        api_response = api_instance.get_feature_view_with_version_api_v1_registry_feature_views_feature_view_name_versions_version_get(feature_view_name, version)
        print("The response of RegistryApi->get_feature_view_with_version_api_v1_registry_feature_views_feature_view_name_versions_version_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RegistryApi->get_feature_view_with_version_api_v1_registry_feature_views_feature_view_name_versions_version_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **feature_view_name** | **str**|  | 
 **version** | **int**|  | 

### Return type

[**FeatureViewOutput**](FeatureViewOutput.md)

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

# **get_latest_feature_view_api_v1_registry_feature_views_feature_view_name_get**
> FeatureViewOutput get_latest_feature_view_api_v1_registry_feature_views_feature_view_name_get(feature_view_name)

Get Latest Feature View

### Example


```python
import openapi_client
from openapi_client.models.feature_view_output import FeatureViewOutput
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
    api_instance = openapi_client.RegistryApi(api_client)
    feature_view_name = 'feature_view_name_example' # str | 

    try:
        # Get Latest Feature View
        api_response = api_instance.get_latest_feature_view_api_v1_registry_feature_views_feature_view_name_get(feature_view_name)
        print("The response of RegistryApi->get_latest_feature_view_api_v1_registry_feature_views_feature_view_name_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RegistryApi->get_latest_feature_view_api_v1_registry_feature_views_feature_view_name_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **feature_view_name** | **str**|  | 

### Return type

[**FeatureViewOutput**](FeatureViewOutput.md)

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

