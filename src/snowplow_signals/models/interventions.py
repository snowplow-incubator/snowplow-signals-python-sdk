from pydantic import EmailStr
from pydantic import Field as PydanticField

from .model import RuleInterventionInput


class RuleIntervention(RuleInterventionInput):
    owner: EmailStr = PydanticField(
        ...,
        description="The owner of the view, typically the email of the primary maintainer. This field is required for view creation.",
        title="Owner",
    )
