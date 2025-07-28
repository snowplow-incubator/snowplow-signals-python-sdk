from .path_translation import path_to_snowflake_syntax
from .utils import BaseSDJProperty, _clean_name, _clean_vendor, _clean_version


class EventProperty(BaseSDJProperty):
    """
    Reference the event properties from an event.
    """

    def _to_api_property(self) -> str:
        path = f":{path_to_snowflake_syntax(self.path)}" if self.path != "" else ""
        return f"unstruct_event_{_clean_vendor(self.vendor)}_{_clean_name(self.name)}_{_clean_version(self.major_version)}{path}"
