from pydantic import BaseModel
from pydantic import Field as PydanticField

from snowplow_signals.models.types import ValueType


class Field(BaseModel):
    """
    A Field represents a set of values with the same structure.
    """

    name: str = PydanticField(description="The name of the field.")

    description: str | None = PydanticField(
        description="A human-readable description.",
        default=None,
    )

    dtype: ValueType = PydanticField(
        description="The type of the field, such as string or float.",
        default="UNKNOWN",
    )

    tags: dict[str, str] | None = PydanticField(
        description="A dictionary of key-value pairs to store arbitrary metadata.",
        default=None,
    )

    vector_index: bool = PydanticField(
        description="If set to True the field will be indexed for vector similarity search.",
        default=False,
    )

    vector_search_metric: str | None = PydanticField(
        description="The metric used for vector similarity search.",
        default=None,
    )
