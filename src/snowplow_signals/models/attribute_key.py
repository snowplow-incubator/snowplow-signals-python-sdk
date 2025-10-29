from pydantic import Field

from .model import AttributeKey as OriginalAttributeKey


class AttributeKey(OriginalAttributeKey):
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
