import json
from typing import Literal, Optional

import httpx

type HTTP_METHODS = Literal["GET", "POST", "PUT", "DELETE"]


class NotFoundException(Exception):
    pass


class ApiClient:

    def __init__(self, api_url: str):
        self.api_url = api_url

    def _get_headers(self):
        # TODO Add Auth headers
        return {"Content-Type": "application/json", "charset": "utf-8"}

    def _request(
        self,
        method: HTTP_METHODS,
        endpoint: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> dict:
        url = f"{self.api_url}/api/v1/{endpoint}"
        response = httpx.request(
            method=method,
            url=url,
            headers=self._get_headers(),
            params=params,
            json=data,
        )

        if response.status_code in (200, 201):
            try:
                return response.json()
            except json.JSONDecodeError:
                raise Exception(f"Failed to decode response: {response.text}")
        try:
            payload = response.json()
            raise Exception(
                f"Request failed with status {response.status_code}: {payload}"
            )
        except (KeyError, ValueError):
            raise Exception(
                f"Request failed with status {response.status_code}: {response.text}"
            )

    def make_request(
        self,
        method: HTTP_METHODS,
        endpoint: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> dict:
        return self._request(method=method, endpoint=endpoint, params=params, data=data)
