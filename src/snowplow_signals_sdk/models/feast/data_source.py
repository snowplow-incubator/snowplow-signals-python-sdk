from typing import Literal, Optional

from beanie import Link
from pydantic import Field as PydanticField

from snowplow_signals_sdk.api_client import ApiClient

from .base_feast_object import BaseFeastObject


class DataSource(BaseFeastObject):
    """
    DataSource that can be used to source features.
    """

    type: Literal["push", "snowflake", "file"] = PydanticField(
        description="The type of data source.",
        default="push",
    )

    timestamp_field: str | None = PydanticField(
        description="Event timestamp field used for point-in-time joins of feature values.",
        default=None,
    )

    created_timestamp_column: str | None = PydanticField(
        description="Timestamp column indicating when the row was created, used for deduplicating rows.",
        default=None,
    )

    field_mapping: dict[str, str] | None = PydanticField(
        description="A dictionary mapping of column names in this data source to feature names in a feature table or view. Only used for feature columns and timestamp columns, not entity columns.",
        default=None,
    )

    date_partition_column: str | None = PydanticField(
        description="Timestamp column used for partitioning. Not supported by all offline stores.",
        default=None,
    )

    # Snowflake datasource fields

    database: str | None = PydanticField(
        description="Snowflake database where the features are stored.",
        default=None,
    )

    schema: str | None = PydanticField(
        description="Snowflake schema in which the table is located.",
        default=None,
    )

    table: str | None = PydanticField(
        description="Snowflake table where the features are stored. Exactly one of 'table' and 'query' must be specified.",
        default=None,
    )

    query: str | None = PydanticField(
        description="The query to be executed to obtain the features. Exactly one of 'table' and 'query' must be specified.",
        default=None,
    )

    # File datasource fields
    path: str | None = PydanticField(
        description="File path to file containing feature data. Must contain an event_timestamp column, entity columns and feature columns.",
        default=None,
    )

    # Push source
    batch_source: str | None = PydanticField(
        description="The id of the batch source that backs this push source. It's used when materializing from the offline store to the online store, and when retrieving historical features",
        default=None,
    )

    def register_to_store(self, api_client: ApiClient) -> Optional["DataSource"]:
        if self.already_registered(api_client=api_client, object_type="data_sources"):
            return self

        response = api_client.make_post_request(
            endpoint="registry/data_sources/", data=self.model_dump(mode="json")
        )
        self.id = response.get("_id", self.id)
        return self
