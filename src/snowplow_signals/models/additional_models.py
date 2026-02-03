from __future__ import annotations

from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field, constr


class TargetAttributeKey(BaseModel):
    name: str = Field(
        ..., description="The name of the entity being targeted.", title="Name"
    )
    id: str = Field(
        ..., description="The identifier for this entity instance.", title="Id"
    )


class InterventionInstance(BaseModel):
    intervention_id: Optional[UUID] = Field(default=None, title="Intervention Id")
    name: constr(pattern=r"^[A-Za-z0-9_]+$", min_length=1, max_length=128) = Field(
        ...,
        description="The unique name of the intervention.",
        examples=["my_intervention"],
        title="Name",
    )
    version: int = Field(..., description="The version of the object.", title="Version")
    target_attribute_key: Optional[TargetAttributeKey] = Field(
        default=None,
        description="The entity instance that triggered this intervention.",
    )
    attributes: Optional[Dict[str, str]] = Field(
        default=None,
        description="Current attributes for the target_attribute_key at the time of this intervention.",
        title="Attributes",
    )
