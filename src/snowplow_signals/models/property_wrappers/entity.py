from pydantic import Field

from .utils import BaseSDJProperty, _clean_name, _clean_vendor, _clean_version


class EntityProperty(BaseSDJProperty):
    """
    Reference an entity field from an event context.
    """

    index: int = Field(
        default=0,
        description="Index of the entity. The :nth entity in the event context.",
    )

    def _to_api_property(self) -> str:
        path = f".{self.path}" if self.path != "" else ""
        return f"contexts_{_clean_vendor(self.vendor)}_{_clean_name(self.name)}_{_clean_version(self.major_version)}[{self.index}]{path}"
