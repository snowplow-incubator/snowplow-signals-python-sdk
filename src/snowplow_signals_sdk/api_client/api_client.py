from pydantic import BaseModel
from enum import Enum
from typing import Optional
from ..settings.connection import ConnectionSettings, DEFAULT_CONNECTION_SETTINGS
import requests


class Methods(Enum):
    get = "get"
    post = "post"
    put = "put"
    delete = "delete"


class ApiClient(BaseModel):
    connection_settings: ConnectionSettings = DEFAULT_CONNECTION_SETTINGS

    def _request(
        self,
        method: Methods,
        endpoint: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
    ):
        url = f"{self.connection_settings.BPD_CONSOLE_API_URL}/{self.connection_settings.BDP_ORG_ID}/{endpoint}"
        # TO-DO Add Auth headers
        headers = {"Content-Type": "application/json"}

        response = requests.request(
            method=method, url=url, headers=headers, params=params, json=data
        )
        response.raise_for_status()
        return response.json()

    def make_get_request(
        self, endpoint: str, params: Optional[dict] = None, data: Optional[dict] = None
    ):
        return self._request(method="get", endpoint=endpoint, params=params, data=data)

    def make_post_request(
        self, endpoint: str, params: Optional[dict] = None, data: Optional[dict] = None
    ):
        return self._request(method="post", endpoint=endpoint, params=params, data=data)


DEFAULT_API_CLIENT = ApiClient()
