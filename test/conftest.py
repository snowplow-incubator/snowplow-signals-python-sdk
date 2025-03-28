import httpx
import jwt
import pytest

from snowplow_signals import Signals

from .utils import MOCK_ORG_ID, utc_timestamp


@pytest.fixture
def signals_client():
    return Signals(
        api_url="http://localhost:8000",
        api_key="foo",
        api_key_id="bar",
        org_id=MOCK_ORG_ID,
    )


@pytest.fixture
def access_jwt():
    """Creates a sample JWT claimset for use as a payload during tests"""
    return jwt.encode(
        {"iss": "peter", "exp": utc_timestamp() + 100, "claim": "foo"}, "secret"
    )


@pytest.fixture(autouse=True)
def mock_auth(respx_mock, request, access_jwt):
    if "noauthmock" in request.keywords:
        return
    respx_mock.get(
        f"https://console.snowplowanalytics.com/api/msc/v1/organizations/{MOCK_ORG_ID}/credentials/v3/token"
    ).mock(return_value=httpx.Response(200, json={"accessToken": access_jwt}))
