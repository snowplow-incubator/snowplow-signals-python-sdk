import pytest
import httpx
from respx import MockRouter

from snowplow_signals import SignalsSandbox
from snowplow_signals.api_client import ApiClient


class TestSandboxAuthentication:
    """Test cases for SANDBOX authentication mode"""

    def test_api_client_sandbox_mode_initialization(self):
        """Test ApiClient initialization with SANDBOX mode"""
        client = ApiClient(
            api_url="http://localhost:8000",
            auth_mode="sandbox",
            sandbox_token="test-token",
        )

        assert client.auth_mode == "sandbox"
        assert client.sandbox_token == "test-token"
        assert client.api_key is None
        assert client.api_key_id is None
        assert client.org_id is None

    def test_api_client_sandbox_mode_missing_token_raises_error(self):
        """Test ApiClient initialization with SANDBOX mode but missing token"""
        with pytest.raises(
            ValueError,
            match="When auth_mode is 'sandbox' a non-empty sandbox_token must be provided",
        ):
            ApiClient(
                api_url="http://localhost:8000", auth_mode="sandbox", sandbox_token=None
            )

    def test_api_client_bdp_mode_missing_credentials_raises_error(self):
        """Test ApiClient initialization with BDP mode but missing credentials"""
        with pytest.raises(
            ValueError,
            match="When auth_mode is 'bdp' api_key, api_key_id, and org_id must be provided",
        ):
            ApiClient(
                api_url="http://localhost:8000",
                auth_mode="bdp",
                api_key=None,
                api_key_id="test",
                org_id="test",
            )

    def test_api_client_sandbox_token_used_directly(self, respx_mock: MockRouter):
        """Test that SANDBOX mode uses the sandbox token directly without fetching"""
        client = ApiClient(
            api_url="http://localhost:8000",
            auth_mode="sandbox",
            sandbox_token="test-sandbox-token",
        )

        # Mock API endpoint
        mock_request = respx_mock.get("http://localhost:8000/api/v1/test").mock(
            return_value=httpx.Response(200, json={"success": True})
        )

        # Make request
        client.make_request("GET", "test")

        # Verify request was made with sandbox token
        assert mock_request.called
        assert mock_request.call_count == 1
        auth_header = mock_request.calls[0].request.headers.get("Authorization")
        assert auth_header == "Bearer test-sandbox-token"

    @pytest.mark.noauthmock
    def test_api_client_sandbox_no_token_fetch_attempted(self, respx_mock: MockRouter):
        """Test that SANDBOX mode doesn't attempt to fetch tokens from console"""
        client = ApiClient(
            api_url="http://localhost:8000",
            auth_mode="sandbox",
            sandbox_token="test-sandbox-token",
        )

        # Mock API endpoint
        respx_mock.get("http://localhost:8000/api/v1/test").mock(
            return_value=httpx.Response(200, json={"success": True})
        )

        # Mock console token endpoint to ensure it's not called
        console_mock = respx_mock.get(
            "https://console.snowplowanalytics.com/api/msc/v1/organizations/test/credentials/v3/token"
        ).mock(
            return_value=httpx.Response(
                200, json={"accessToken": "should-not-be-called"}
            )
        )

        # Make request
        client.make_request("GET", "test")

        # Verify console endpoint was not called
        assert not console_mock.called

    def test_signals_sandbox_mode_initialization(self):
        """Test Signals initialization with SANDBOX mode"""
        signals = SignalsSandbox(
            api_url="http://localhost:8000",
            sandbox_token="test-token",
        )

        assert signals.api_client.auth_mode == "sandbox"
        assert signals.api_client.sandbox_token == "test-token"

    def test_signals_sandbox_mode_missing_token_raises_error(self):
        """Test Signals initialization with SANDBOX mode but missing token"""
        with pytest.raises(
            ValueError,
            match="When auth_mode is 'sandbox' a non-empty sandbox_token must be provided",
        ):
            SignalsSandbox(
                api_url="http://localhost:8000",
                sandbox_token=None,  # type: ignore
            )

    def test_signals_sandbox_mode_api_calls(self, respx_mock: MockRouter):
        """Test that Signals with SANDBOX mode makes successful API calls"""
        signals = SignalsSandbox(
            api_url="http://localhost:8000",
            sandbox_token="test-sandbox-token",
        )

        # Mock interventions endpoint
        interventions_mock = respx_mock.get(
            "http://localhost:8000/api/v1/registry/interventions/"
        ).mock(return_value=httpx.Response(200, json=[]))

        # Call interventions list
        result = signals.interventions.list()

        # Verify call was made with correct auth
        assert interventions_mock.called
        auth_header = interventions_mock.calls[0].request.headers.get("Authorization")
        assert auth_header == "Bearer test-sandbox-token"
        assert result == []

    def test_bdp_auth_mode_compatibility(self):
        """Test that default BDP mode still works"""
        # This should work without specifying auth_mode
        client = ApiClient(
            api_url="http://localhost:8000",
            api_key="test",
            api_key_id="test",
            org_id="test",
        )

        assert client.auth_mode == "bdp"
        assert client.api_key == "test"
        assert client.api_key_id == "test"
        assert client.org_id == "test"
