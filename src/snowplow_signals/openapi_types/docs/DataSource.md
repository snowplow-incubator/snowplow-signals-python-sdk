# DataSource

DataSource that can be used to source features.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The unique name of the object. | 
**type** | **str** | The type of data source. | [optional] [default to 'push']
**timestamp_field** | **str** |  | [optional] 
**created_timestamp_column** | **str** |  | [optional] 
**field_mapping** | **Dict[str, str]** |  | [optional] 
**description** | **str** |  | [optional] 
**tags** | **Dict[str, str]** |  | [optional] 
**owner** | **str** |  | [optional] 
**date_partition_column** | **str** |  | [optional] 
**database** | **str** |  | [optional] 
**var_schema** | **str** |  | [optional] 
**table** | **str** |  | [optional] 
**query** | **str** |  | [optional] 
**path** | **str** |  | [optional] 
**batch_source** | [**DataSourceLink**](DataSourceLink.md) |  | [optional] 

## Example

```python
from openapi_client.models.data_source import DataSource

# TODO update the JSON string below
json = "{}"
# create an instance of DataSource from a JSON string
data_source_instance = DataSource.from_json(json)
# print the JSON string representation of the object
print(DataSource.to_json())

# convert the object into a dict
data_source_dict = data_source_instance.to_dict()
# create an instance of DataSource from a dict
data_source_from_dict = DataSource.from_dict(data_source_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


