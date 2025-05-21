from pydantic import Field, BeforeValidator
from typing import Annotated
from .model import (
    Service as ServiceInput,
    VersionedLinkView,
)
from .view import View
from pydantic import EmailStr

def view_to_link(
    views: list[View | VersionedLinkView | dict] | None,
) -> list[VersionedLinkView | dict] | None:
    if views:
        views = [
            (
                VersionedLinkView(name=view.name, version=view.version)
                if isinstance(view, View)
                else view
            )
            for view in views
        ]
    return views


class Service(ServiceInput):
    views: Annotated[list[VersionedLinkView | View], BeforeValidator(view_to_link)] = (
        Field(
            None,
            description="A list containing views, representing the features in the service.",
            max_length=100,
            min_length=1,
            title="Views",
        )  # type: ignore[assignment]
    )
    owner: EmailStr = Field(
        ...,
        description="The owner of the service, typically the email of the primary maintainer. This field is required for service creation.",
        title="Owner",
    )
