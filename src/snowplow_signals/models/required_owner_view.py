from pydantic import Field, EmailStr
from .view import View


class RequiredOwnerView(View):
    """
    A View class that requires the owner field to be set.
    This is used specifically for view creation to enforce owner attribution.
    """
    owner: EmailStr = Field(
        ...,
        description="The owner of the view, typically the email of the primary maintainer. This field is required for view creation.",
        title="Owner",
    ) 