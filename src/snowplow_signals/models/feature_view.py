from datetime import timedelta
from typing import Literal, Optional, Union

from pydantic import Field as PydanticField
from pydantic import computed_field

from snowplow_signals.api_client import ApiClient, NotFoundException
from snowplow_signals.models.feature import Feature
from snowplow_signals.models.field import Field

from .base_signals_object import BaseSignalsObject
from .data_source import DataSource
from .entity import Entity


class FeatureView(BaseSignalsObject):
    """
    A FeatureView defines a logical group of features.
    """

    version: int = PydanticField(
        description="The version of the feature view.",
        default=1,
    )

    entities: list[Entity] = PydanticField(
        description="The list of ids of entities that this feature view is associated with.",
        default_factory=list,
    )

    ttl: timedelta | None = PydanticField(
        description="The amount of time this group of features lives. A ttl of 0 indicates that this group of features lives forever. Note that large ttl's or a ttl of 0 can result in extremely computationally intensive queries.",
        default_factory=lambda: timedelta(days=0),
    )

    source: Union[str, DataSource] | None = PydanticField(
        description="""The id of the data source for this group of features. May be a stream source, or a batch source.
                        If a stream source, the source should contain a batch_source for backfills & batch materialization.""",
        default=None,
    )

    online: bool = PydanticField(
        description="A boolean indicating whether online retrieval is enabled for this feature view.",
        default=True,
    )

    fields: list[Field] = PydanticField(
        description="The schema of the feature view, including timestamp, and entity columns. If not specified, can be inferred from the underlying data source.",
        default_factory=list,
    )

    features: list[Feature] = PydanticField(
        description="The list of features that this feature view is associated with.",
        default_factory=list,
    )

    status: Literal["Draft", "QA", "Live"] = PydanticField(
        description="The status of the feature view.",
        default="Live",
    )

    @computed_field
    @property
    def feast_name(self) -> str:
        return f"{self.name}_v{self.version}"

    def register_to_store(self, api_client: ApiClient) -> Optional["FeatureView"]:
        for entity in self.entities:
            entity.register_to_store(api_client)

        try:
            response = api_client.make_get_request(
                endpoint=f"registry/feature_views/{self.name}/versions/{self.version}"
            )
        except NotFoundException:
            response = api_client.make_post_request(
                endpoint="registry/feature_views/", data=self.model_dump(mode="json")
            )

        response = FeatureView.model_validate(response)
        self.__dict__.update(response)

        return self
