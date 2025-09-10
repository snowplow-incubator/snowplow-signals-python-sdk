import pytest
import httpx
from respx import MockRouter

from snowplow_signals import Signals
from snowplow_signals.api_client import ApiClient


class TestTrialAuthentication:
    """Test cases for TRIAL authentication mode"""

    def test_api_client_trial_mode_initialization(self):
        """Test ApiClient initialization with TRIAL mode"""
        client = ApiClient(
            api_url="http://localhost:8000",
            auth_mode="trial",
            trial_token="test-token"
        )
        
        assert client.auth_mode == "trial"
        assert client.trial_token == "test-token"
        assert client.api_key is None
        assert client.api_key_id is None
        assert client.org_id is None

    def test_api_client_trial_mode_missing_token_raises_error(self):
        """Test ApiClient initialization with TRIAL mode but missing token"""
        with pytest.raises(ValueError, match="When auth_mode is 'trial' a non-empty trial_token must be provided"):
            ApiClient(
                api_url="http://localhost:8000",
                auth_mode="trial",
                trial_token=None
            )

    def test_api_client_bdp_mode_missing_credentials_raises_error(self):
        """Test ApiClient initialization with BDP mode but missing credentials"""
        with pytest.raises(ValueError, match="When auth_mode is 'bdp' api_key, api_key_id, and org_id must be provided"):
            ApiClient(
                api_url="http://localhost:8000",
                auth_mode="bdp",
                api_key=None,
                api_key_id="test",
                org_id="test"
            )

    def test_api_client_trial_token_used_directly(self, respx_mock: MockRouter):
        """Test that TRIAL mode uses the trial token directly without fetching"""
        client = ApiClient(
            api_url="http://localhost:8000",
            auth_mode="trial",
            trial_token="test-trial-token"
        )
        
        # Mock API endpoint
        mock_request = respx_mock.get("http://localhost:8000/api/v1/test").mock(
            return_value=httpx.Response(200, json={"success": True})
        )
        
        # Make request
        client.make_request("GET", "test")
        
        # Verify request was made with trial token
        assert mock_request.called
        assert mock_request.call_count == 1
        auth_header = mock_request.calls[0].request.headers.get("Authorization")
        assert auth_header == "Bearer test-trial-token"

    @pytest.mark.noauthmock
    def test_api_client_trial_no_token_fetch_attempted(self, respx_mock: MockRouter):
        """Test that TRIAL mode doesn't attempt to fetch tokens from console"""
        client = ApiClient(
            api_url="http://localhost:8000",
            auth_mode="trial",
            trial_token="test-trial-token"
        )
        
        # Mock API endpoint
        respx_mock.get("http://localhost:8000/api/v1/test").mock(
            return_value=httpx.Response(200, json={"success": True})
        )
        
        # Mock console token endpoint to ensure it's not called
        console_mock = respx_mock.get(
            "https://console.snowplowanalytics.com/api/msc/v1/organizations/test/credentials/v3/token"
        ).mock(return_value=httpx.Response(200, json={"accessToken": "should-not-be-called"}))
        
        # Make request
        client.make_request("GET", "test")
        
        # Verify console endpoint was not called
        assert not console_mock.called

    def test_signals_trial_mode_initialization(self):
        """Test Signals initialization with TRIAL mode"""
        signals = Signals(
            api_url="http://localhost:8000",
            auth_mode="trial",
            trial_token="test-token"
        )
        
        assert signals.api_client.auth_mode == "trial"
        assert signals.api_client.trial_token == "test-token"

    def test_signals_trial_mode_missing_token_raises_error(self):
        """Test Signals initialization with TRIAL mode but missing token"""
        with pytest.raises(ValueError, match="When auth_mode is 'trial' a non-empty trial_token must be provided"):
            Signals(
                api_url="http://localhost:8000",
                auth_mode="trial",
                trial_token=None
            )

    def test_signals_bdp_mode_missing_credentials_raises_error(self):
        """Test Signals initialization with BDP mode but missing credentials"""
        with pytest.raises(ValueError, match="When auth_mode is 'bdp' api_key, api_key_id, and org_id must be provided"):
            Signals(
                api_url="http://localhost:8000",
                auth_mode="bdp",
                api_key=None
            )

    def test_signals_trial_mode_api_calls(self, respx_mock: MockRouter):
        """Test that Signals with TRIAL mode makes successful API calls"""
        signals = Signals(
            api_url="http://localhost:8000",
            auth_mode="trial",
            trial_token="test-trial-token"
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
        assert auth_header == "Bearer test-trial-token"
        assert result == []

    def test_check_token_trial_mode_returns_trial_token(self):
        """Test that _check_token returns trial token in TRIAL mode"""
        client = ApiClient(
            api_url="http://localhost:8000",
            auth_mode="trial",
            trial_token="test-trial-token"
        )
        
        # Should return trial token regardless of input
        assert client._check_token(None) == "test-trial-token"
        assert client._check_token("some-other-token") == "test-trial-token"

    def test_trial_mode_backwards_compatibility(self):
        """Test that default BDP mode still works for backwards compatibility"""
        # This should work without specifying auth_mode
        client = ApiClient(
            api_url="http://localhost:8000",
            api_key="test",
            api_key_id="test",
            org_id="test"
        )
        
        assert client.auth_mode == "bdp"
        assert client.api_key == "test"
        assert client.api_key_id == "test"
        assert client.org_id == "test"