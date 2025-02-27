from pydantic import BaseModel


class ConnectionSettings(BaseModel):
    SIGNALS_API_URL: str = (
        "http://localhost:8000"  # Will change depending on where API is hosted
    )

    def __init__(self, SIGNALS_API_URL: str = SIGNALS_API_URL):
        super().__init__()
        self.SIGNALS_API_URL = SIGNALS_API_URL


DEFAULT_CONNECTION_SETTINGS = ConnectionSettings()
