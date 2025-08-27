import json
import os
from collections.abc import Generator, Mapping
from importlib.metadata import version
from typing import Literal, Optional

import httpx
import jwt

HTTP_METHODS = Literal["GET", "POST", "PUT", "DELETE"]

X_SIGNALS_SDK_NAME = f"signals-py {version('snowplow-signals')}"


class ApiClient:
    def __init__(self, api_url: str, api_key: str, api_key_id: str, org_id: str):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.api_key_id = api_key_id
        self.org_id = org_id
        self.token = None

    def _get_headers(self, token: str, custom: Optional[dict[str, str]] = None):
        return {
            **(custom or {}),
            "Content-Type": "application/json; charset=utf-8",
            "X-Signals-Sdk-Name": X_SIGNALS_SDK_NAME,
            "Authorization": f"Bearer {token}",
        }

    def _fetch_token(self) -> str:
        access_token_url = (
            f"https://console.snowplowanalytics.com/api/msc/v1/organizations/{self.org_id}/credentials/v3/token"
            if os.getenv("BDP_NEXT") is None
            else f"https://next.console.snowplowanalytics.com/api/msc/v1/organizations/{self.org_id}/credentials/v3/token"
        )

        response = (
            httpx.get(
                access_token_url,
                headers={
                    "X-API-Key-Id": self.api_key_id,
                    "X-API-Key": self.api_key,
                    "X-Signals-Sdk-Name": X_SIGNALS_SDK_NAME,
                },
            )
            .raise_for_status()
            .json()
        )

        return response["accessToken"]

    def _check_token(self, token: str | None):
        if token is None:
            return self._fetch_token()
        else:
            try:
                jwt.decode(
                    token, options={"verify_signature": False, "verify_exp": True}
                )
                return token
            except jwt.ExpiredSignatureError:
                return self._fetch_token()

    def _request(
        self,
        method: HTTP_METHODS,
        endpoint: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> dict:
        token = self._check_token(self.token)
        self.token = token

        url = f"{self.api_url}/api/v1/{endpoint}"
        response = httpx.request(
            method=method,
            url=url,
            headers=self._get_headers(token),
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

    def _stream_request(
        self,
        method: HTTP_METHODS,
        endpoint: str,
        params: Optional[Mapping[str, str | list[str]]] = None,
        data: Optional[dict] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> Generator[str | None]:
        token = self._check_token(self.token)
        self.token = token

        url = f"{self.api_url}/api/v1/{endpoint}"

        with httpx.stream(
            method=method,
            url=url,
            headers=self._get_headers(token, headers),
            params=params,
            json=data,
        ) as stream:
            if stream.status_code == 200:
                gen = stream.iter_lines()

                # we need to manually consume the iterator to handle the timeout for each call
                while True:
                    try:
                        line = next(gen)
                        yield line
                    except httpx.ReadTimeout:
                        # yield empty result so we can check if the request should be killed
                        yield None
                    except StopIteration:
                        # connection likely killed
                        break
            else:
                try:
                    stream.read()
                    payload = stream.json()
                    raise SignalsAPIError(stream.status_code, payload)
                except json.JSONDecodeError:
                    raise SignalsAPIError(
                        stream.status_code, f"Failed to decode response: {stream.text}"
                    )

    def make_request(
        self,
        method: HTTP_METHODS,
        endpoint: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> dict:
        return self._request(method=method, endpoint=endpoint, params=params, data=data)

    def make_stream_request(
        self,
        method: HTTP_METHODS,
        endpoint: str,
        params: Optional[Mapping[str, str | list[str]]] = None,
        data: Optional[dict[str, object]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> Generator[str | None]:
        return self._stream_request(
            method=method, endpoint=endpoint, params=params, data=data, headers=headers
        )


class SignalsAPIError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        msg = "[Signals API] {0}: {1}"
        return msg.format(self.status_code, self.message)
