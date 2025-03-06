# DataSourceLink


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of data source, which should be unique within a project | 

## Example

```python
from openapi_client.models.data_source_link import DataSourceLink

# TODO update the JSON string below
json = "{}"
# create an instance of DataSourceLink from a JSON string
data_source_link_instance = DataSourceLink.from_json(json)
# print the JSON string representation of the object
print(DataSourceLink.to_json())

# convert the object into a dict
data_source_link_dict = data_source_link_instance.to_dict()
# create an instance of DataSourceLink from a dict
data_source_link_from_dict = DataSourceLink.from_dict(data_source_link_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


