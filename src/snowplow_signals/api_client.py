from enum import Enum
from typing import Optional

import requests
from pydantic import BaseModel

from .settings.connection import DEFAULT_CONNECTION_SETTINGS, ConnectionSettings


class Methods(Enum):
    get = "get"
    post = "post"
    put = "put"
    delete = "delete"


class NotFoundException(Exception):
    pass


class ApiClient(BaseModel):
    connection_settings: ConnectionSettings = DEFAULT_CONNECTION_SETTINGS

    def __init__(self, connection_settings: Optional[ConnectionSettings] = None):
        super().__init__()
        self.connection_settings = connection_settings or DEFAULT_CONNECTION_SETTINGS

    def _request(
        self,
        method: Methods,
        endpoint: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> dict:
        url = f"{self.connection_settings.SIGNALS_API_URL}/api/v1/{endpoint}"
        # TO-DO Add Auth headers
        headers = {"Content-Type": "application/json", "charset": "utf-8"}
        response = requests.request(
            method=method, url=url, headers=headers, params=params, json=data
        )

        if response.status_code == 404:
            raise NotFoundException()
        elif response.status_code != 200:
            raise Exception(
                f"Request failed with status code {response.status_code}, {response.text}"
            )
        else:
            return response.json()

    def make_get_request(
        self, endpoint: str, params: Optional[dict] = None, data: Optional[dict] = None
    ) -> dict:
        return self._request(
            method=Methods.get, endpoint=endpoint, params=params, data=data
        )

    def make_post_request(
        self, endpoint: str, params: Optional[dict] = None, data: Optional[dict] = None
    ) -> dict:
        return self._request(
            method=Methods.post, endpoint=endpoint, params=params, data=data
        )


DEFAULT_API_CLIENT = ApiClient()
