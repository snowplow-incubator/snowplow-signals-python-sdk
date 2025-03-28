import httpx
import jwt
import pytest

from ..utils import MOCK_ORG_ID, utc_timestamp


@pytest.fixture
def payload():
    """Creates a sample JWT claimset for use as a payload during tests"""
    return {"iss": "peter", "exp": utc_timestamp() + 15, "claim": "foo"}


@pytest.mark.noauthmock
def test_client_fetches_and_adds_auth(respx_mock, payload, signals_client):
    jwt_token = jwt.encode(payload, "secret")
    token_request = respx_mock.get(
        f"https://console.snowplowanalytics.com/api/msc/v1/organizations/{MOCK_ORG_ID}/credentials/v3/token"
    ).mock(return_value=httpx.Response(200, json={"accessToken": jwt_token}))

    prompts_request = respx_mock.get("http://localhost:8000/api/v1/prompts/").mock(
        return_value=httpx.Response(200, json=[])
    )
    signals_client.prompts.list()

    assert token_request.called
    assert token_request.call_count == 1
    assert token_request.calls[0].request.headers["X-API-Key-Id"] == "bar"
    assert token_request.calls[0].request.headers["X-API-Key"] == "foo"
    assert (
        prompts_request.calls[0].request.headers["Authorization"]
        == f"Bearer {jwt_token}"
    )

    # Token is valid, will use it
    signals_client.prompts.list()
    assert token_request.call_count == 1


@pytest.mark.noauthmock
def test_client_api_client_expire_token(respx_mock, payload, signals_client):
    payload["exp"] = utc_timestamp() - 15
    expired_jwt_token = jwt.encode(payload, "secret")
    token_request = respx_mock.get(
        f"https://console.snowplowanalytics.com/api/msc/v1/organizations/{MOCK_ORG_ID}/credentials/v3/token"
    ).mock(return_value=httpx.Response(200, json={"accessToken": expired_jwt_token}))

    respx_mock.get("http://localhost:8000/api/v1/prompts/").mock(
        return_value=httpx.Response(200, json=[])
    )
    signals_client.prompts.list()

    assert token_request.called
    assert token_request.call_count == 1

    # Token is expired, will fetch a new token
    signals_client.prompts.list()
    assert token_request.call_count == 2
