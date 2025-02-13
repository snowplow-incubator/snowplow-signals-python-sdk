import os

from pydantic import BaseModel


class ConnectionSettings(BaseModel):
    BPD_CONSOLE_API_URL: str = (
        "http://localhost:8000/api/v1"  # Will change depending on where API is hosted
    )


DEFAULT_CONNECTION_SETTINGS = ConnectionSettings()
