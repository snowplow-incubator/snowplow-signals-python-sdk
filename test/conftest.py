import httpx
import pytest

from snowplow_signals import Signals

from .utils import MOCK_ORG_ID


@pytest.fixture
def signals_client():
    return Signals(
        api_url="http://localhost:8000",
        api_key="foo",
        api_key_id="bar",
        org_id=MOCK_ORG_ID,
    )


@pytest.fixture(autouse=True)
def mock_auth(respx_mock, request):
    if "noauthmock" in request.keywords:
        return
    respx_mock.get(
        f"https://console.snowplowanalytics.com/api/msc/v1/organizations/{MOCK_ORG_ID}/credentials/v3/token"
    ).mock(return_value=httpx.Response(200, json={"accessToken": "jwt_token"}))
