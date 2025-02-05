import os

from pydantic import BaseModel


class ConnectionSettings(BaseModel):
    BDP_ORG_ID: str = os.environ.get("BDP_ORG_ID")
    BPD_CONSOLE_API_URL: str = (
        "localhost:8000/api/v1/"  # Will change depending on where API is hosted
    )


DEFAULT_CONNECTION_SETTINGS = ConnectionSettings()
