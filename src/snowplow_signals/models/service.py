from pydantic import Field, BeforeValidator
from typing import Annotated
from .model import (
    Service as ServiceInput,
    VersionedLinkView,
)
from .view import View


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
        )
    )
