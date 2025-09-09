from pydantic import EmailStr
from pydantic import Field as PydanticField

from .model import RuleInterventionInput


class RuleIntervention(RuleInterventionInput):
    owner: EmailStr = PydanticField(
        ...,
        description="The owner of the intervention, typically the email of the primary maintainer. This field is required for intervention creation.",
        title="Owner",
    )
