from typing import Any

from pydantic import Field

from .model import AtomicProperty, AttributeKeyInput, EntityProperty, EventProperty

SNOWPLOW_ID = "snowplow_id"

# The API refuses to update a built-in key unless its key and property match.
SNOWPLOW_ID_PROPERTY = EntityProperty(
    vendor="com.snowplowanalytics.snowplow",
    name="identity",
    major_version=2,
    path="snowplow_id",
)


class AttributeKey(AttributeKeyInput):
    key: str | None = Field(
        default=None,
        description="Deprecated: The key used to join this entity to an attribute table. If not specified, the name is used.",
        examples=["domain_sessionid"],
        title="Key (Deprecated)",
        pattern=r"^[A-Za-z0-9_]+$",
        min_length=1,
        max_length=128,
        deprecated=True,
    )

    name: str | None = Field(
        default=None,
        description="Optional: Derived from `property` or `external_column` fields. The unique name of the attribute key.",
        examples=["domain_sessionid"],
        title="Name",
        pattern=r"^[A-Za-z0-9_]+$",
        min_length=1,
        max_length=128,
    )

    def model_post_init(self, context: Any) -> None:
        # Checks model_fields_set because reading the deprecated key field warns.
        if (
            self.name == SNOWPLOW_ID
            and "key" not in self.model_fields_set
            and self.property is None
        ):
            self.key = SNOWPLOW_ID
            self.property = SNOWPLOW_ID_PROPERTY.model_copy()
            if self.description is None:
                self.description = (
                    "The Snowplow ID that Identities resolved the user to"
                )
        if self.name and self.external_column and self.name != self.external_column:
            raise ValueError(
                "If external_column is specified, it must be equal to the name of the AttributeKey."
            )
        if self.name is None:
            if self.external_column:
                self.name = self.external_column
            elif isinstance(self.property, AtomicProperty):
                self.name = self.property.name
            elif isinstance(self.property, (EventProperty, EntityProperty)):
                self.name = self.property.path.split(".")[-1]
            elif self.key and self.name is None:
                raise ValueError(
                    "Name could not be derived from key only. Please provide a name explicitly or use the property or external_column fields."
                )
            else:
                raise ValueError("Name should be provided if no other fields are set.")
