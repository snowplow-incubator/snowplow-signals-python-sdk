from enum import Enum
from typing import Any, Optional

import requests
from pydantic import BaseModel

from .settings.connection import DEFAULT_CONNECTION_SETTINGS, ConnectionSettings


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
    ) -> Any:
        url = f"{self.connection_settings.BPD_CONSOLE_API_URL}/{endpoint}"
        # TO-DO Add Auth headers
        headers = {"Content-Type": "application/json", "charset": "utf-8"}
        response = requests.request(
            method=method, url=url, headers=headers, params=params, json=data
        )
        return response.json()

    def make_get_request(
        self, endpoint: str, params: Optional[dict] = None, data: Optional[dict] = None
    ) -> Any:
        return self._request(method="get", endpoint=endpoint, params=params, data=data)

    def make_post_request(
        self, endpoint: str, params: Optional[dict] = None, data: Optional[dict] = None
    ) -> Any:
        return self._request(method="post", endpoint=endpoint, params=params, data=data)


DEFAULT_API_CLIENT = ApiClient()
