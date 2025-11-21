from typing import Any

from pydantic import Field

from .model import AtomicProperty, AttributeKeyInput, EntityProperty, EventProperty


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
        if self.name and self.external_column and self.name != self.external_column:
            raise ValueError(
                "If external_column is specified, it must be equal to the name of the AttributeKey."
            )
        if self.name is None and (
            self.property is not None
            or self.external_column is not None
            or self.key is not None
        ):
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
