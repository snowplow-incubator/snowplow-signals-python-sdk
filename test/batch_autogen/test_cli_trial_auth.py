import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from snowplow_signals.batch_autogen.cli import app, create_api_client


class TestCLITrialAuth:
    """Test cases for CLI commands with TRIAL authentication"""

    def test_create_api_client_with_trial_auth(self):
        """Test create_api_client function with TRIAL auth parameters"""
        client = create_api_client(
            api_url="http://localhost:8000",
            api_key=None,
            api_key_id=None,
            org_id=None,
            auth_mode="trial",
            trial_token="test-trial-token"
        )
        
        assert client.auth_mode == "trial"
        assert client.trial_token == "test-trial-token"
        assert client.api_key is None
        assert client.api_key_id is None
        assert client.org_id is None

    def test_create_api_client_with_bdp_auth(self):
        """Test create_api_client function with BDP auth parameters"""
        client = create_api_client(
            api_url="http://localhost:8000",
            api_key="test-key",
            api_key_id="test-key-id",
            org_id="test-org",
            auth_mode="bdp",
            trial_token=None
        )
        
        assert client.auth_mode == "bdp"
        assert client.api_key == "test-key"
        assert client.api_key_id == "test-key-id"
        assert client.org_id == "test-org"
        assert client.trial_token is None

    @patch('snowplow_signals.batch_autogen.cli.BatchAutogenClient')
    def test_cli_init_with_trial_auth_env_vars(self, mock_client_class):
        """Test CLI init command with TRIAL auth via environment variables"""
        runner = CliRunner()
        
        # Mock the client
        mock_client = MagicMock()
        mock_client.init_project.return_value = True
        mock_client_class.return_value = mock_client
        
        with patch.dict('os.environ', {
            'SNOWPLOW_API_URL': 'http://localhost:8000',
            'SNOWPLOW_AUTH_MODE': 'trial',
            'SNOWPLOW_TRIAL_TOKEN': 'test-trial-token',
            'SNOWPLOW_REPO_PATH': '/tmp/test',
            'SNOWPLOW_TARGET_TYPE': 'snowflake'
        }):
            result = runner.invoke(app, ['init'])
            
            # Verify command succeeded
            assert result.exit_code == 0
            assert "Successfully initialized dbt project(s)" in result.stdout
            
            # Verify client was created with correct auth mode
            mock_client_class.assert_called_once()
            call_args = mock_client_class.call_args
            api_client = call_args[1]['api_client']
            assert api_client.auth_mode == "trial"
            assert api_client.trial_token == "test-trial-token"

    @patch('snowplow_signals.batch_autogen.cli.BatchAutogenClient')
    def test_cli_init_with_trial_auth_flags(self, mock_client_class):
        """Test CLI init command with TRIAL auth via command line flags"""
        runner = CliRunner()
        
        # Mock the client
        mock_client = MagicMock()
        mock_client.init_project.return_value = True
        mock_client_class.return_value = mock_client
        
        result = runner.invoke(app, [
            'init',
            '--api-url', 'http://localhost:8000',
            '--auth-mode', 'trial',
            '--trial-token', 'test-trial-token',
            '--repo-path', '/tmp/test',
            '--target-type', 'snowflake'
        ])
        
        # Verify command succeeded
        assert result.exit_code == 0
        assert "Successfully initialized dbt project(s)" in result.stdout
        
        # Verify client was created with correct auth mode
        mock_client_class.assert_called_once()
        call_args = mock_client_class.call_args
        api_client = call_args[1]['api_client']
        assert api_client.auth_mode == "trial"
        assert api_client.trial_token == "test-trial-token"

    @patch('snowplow_signals.batch_autogen.cli.BatchAutogenClient')
    def test_cli_generate_with_trial_auth(self, mock_client_class):
        """Test CLI generate command with TRIAL auth"""
        runner = CliRunner()
        
        # Mock the client
        mock_client = MagicMock()
        mock_client.generate_models.return_value = True
        mock_client_class.return_value = mock_client
        
        result = runner.invoke(app, [
            'generate',
            '--api-url', 'http://localhost:8000',
            '--auth-mode', 'trial',
            '--trial-token', 'test-trial-token',
            '--repo-path', '/tmp/test',
            '--target-type', 'bigquery'
        ])
        
        # Verify command succeeded
        assert result.exit_code == 0
        assert "Successfully generated dbt models" in result.stdout
        
        # Verify client was created with correct auth mode
        mock_client_class.assert_called_once()
        call_args = mock_client_class.call_args
        api_client = call_args[1]['api_client']
        assert api_client.auth_mode == "trial"
        assert api_client.trial_token == "test-trial-token"


    def test_cli_init_missing_trial_token_error(self):
        """Test CLI init command fails when TRIAL mode is specified but token is missing"""
        runner = CliRunner()
        
        result = runner.invoke(app, [
            'init',
            '--api-url', 'http://localhost:8000',
            '--auth-mode', 'trial',
            '--repo-path', '/tmp/test',
            '--target-type', 'snowflake'
        ])
        
        # Verify command failed
        assert result.exit_code == 1
        assert "Error during project initialization" in result.stdout

    def test_cli_init_missing_bdp_credentials_error(self):
        """Test CLI init command fails when BDP mode is specified but credentials are missing"""
        runner = CliRunner()
        
        result = runner.invoke(app, [
            'init',
            '--api-url', 'http://localhost:8000',
            '--auth-mode', 'bdp',
            '--repo-path', '/tmp/test',
            '--target-type', 'snowflake'
        ])
        
        # Verify command failed
        assert result.exit_code == 1
        assert "Error during project initialization" in result.stdout