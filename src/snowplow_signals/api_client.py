import json
from typing import Literal, Optional

import httpx

type HTTP_METHODS = Literal["GET", "POST", "PUT", "DELETE"]


class ApiClient:

    def __init__(self, api_url: str):
        self.api_url = api_url

    def _get_headers(self):
        # TODO Add Auth headers
        return {"Content-Type": "application/json; charset=utf-8"}

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
            timeout=30.0,
        )

        if response.status_code in (200, 201):
            try:
                return response.json()
            except json.JSONDecodeError:
                raise SignalsAPIError(
                    response.status_code, f"Failed to decode response: {response.text}"
                )
        try:
            payload = response.json()
            raise SignalsAPIError(response.status_code, payload)
        except (KeyError, ValueError):
            raise SignalsAPIError(
                response.status_code, f"Failed to decode response: {response.text}"
            )

    def make_request(
        self,
        method: HTTP_METHODS,
        endpoint: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> dict:
        return self._request(method=method, endpoint=endpoint, params=params, data=data)


class SignalsAPIError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        msg = "[Signals API] {0}: {1}"
        return msg.format(self.status_code, self.message)
