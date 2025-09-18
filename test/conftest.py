import httpx
import jwt
import pytest
from pytest import FixtureRequest
from respx import MockRouter

from snowplow_signals import Signals
from snowplow_signals.api_client import ApiClient

from .utils import (
    MOCK_API_KEY,
    MOCK_API_KEY_ID,
    MOCK_API_URL,
    MOCK_ORG_ID,
    utc_timestamp,
)


@pytest.fixture
def api_params() -> list[str]:
    """Common API parameters for testing."""
    return [
        "--api-url",
        MOCK_API_URL,
        "--api-key",
        MOCK_API_KEY,
        "--api-key-id",
        MOCK_API_KEY_ID,
        "--org-id",
        MOCK_ORG_ID,
    ]


@pytest.fixture
def signals_client() -> Signals:
    return Signals(
        api_url="http://localhost:8000",
        api_key="foo",
        api_key_id="bar",
        org_id=MOCK_ORG_ID,
    )


@pytest.fixture
def signals_client_sandbox() -> Signals:
    return Signals(
        api_url="http://localhost:8000",
        auth_mode="sandbox",
        sandbox_token="test-sandbox-token",
    )


@pytest.fixture
def access_jwt() -> str:
    """Creates a sample JWT claimset for use as a payload during tests"""
    return jwt.encode(
        {"iss": "peter", "exp": utc_timestamp() + 100, "claim": "foo"}, "secret"
    )


@pytest.fixture(autouse=True)
def mock_auth(respx_mock: MockRouter, request: FixtureRequest, access_jwt: str):
    if "noauthmock" in request.keywords:
        return
    respx_mock.get(
        f"https://console.snowplowanalytics.com/api/msc/v1/organizations/{MOCK_ORG_ID}/credentials/v3/token"
    ).mock(return_value=httpx.Response(200, json={"accessToken": access_jwt}))


@pytest.fixture
def api_client() -> ApiClient:
    return ApiClient(
        api_url="http://localhost:8000",
        api_key="foo",
        api_key_id="bar",
        org_id=MOCK_ORG_ID,
    )


@pytest.fixture
def api_client_sandbox() -> ApiClient:
    return ApiClient(
        api_url="http://localhost:8000",
        auth_mode="sandbox",
        sandbox_token="test-sandbox-token",
    )


@pytest.fixture
def mock_successful_api_health(respx_mock: MockRouter):
    """Mock successful API health check response."""
    respx_mock.get(f"{MOCK_API_URL}/health-all").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "ok",
                "dependencies": {"storage": "ok", "feature_server": "ok"},
            },
        )
    )


@pytest.fixture
def mock_successful_registry_groups(respx_mock: MockRouter):
    """Mock successful registry views response."""
    respx_mock.get(f"{MOCK_API_URL}/api/v1/registry/attribute_groups/").mock(
        return_value=httpx.Response(
            200,
            json=[],
        )
    )
