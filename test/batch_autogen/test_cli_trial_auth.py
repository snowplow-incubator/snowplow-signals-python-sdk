import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from snowplow_signals.batch_autogen.cli import app, create_api_client


class TestCLISandboxAuth:
    """Test cases for CLI commands with SANDBOX authentication"""

    def test_create_api_client_with_sandbox_auth(self):
        """Test create_api_client function with SANDBOX auth parameters"""
        client = create_api_client(
            api_url="http://localhost:8000",
            api_key=None,
            api_key_id=None,
            org_id=None,
            auth_mode="sandbox",
            sandbox_token="test-sandbox-token"
        )
        
        assert client.auth_mode == "sandbox"
        assert client.sandbox_token == "test-sandbox-token"
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
            sandbox_token=None
        )
        
        assert client.auth_mode == "bdp"
        assert client.api_key == "test-key"
        assert client.api_key_id == "test-key-id"
        assert client.org_id == "test-org"
        assert client.sandbox_token is None

    @patch('snowplow_signals.batch_autogen.cli.BatchAutogenClient')
    def test_cli_init_with_sandbox_auth_env_vars(self, mock_client_class):
        """Test CLI init command with SANDBOX auth via environment variables"""
        runner = CliRunner()
        
        # Mock the client
        mock_client = MagicMock()
        mock_client.init_project.return_value = True
        mock_client_class.return_value = mock_client
        
        with patch.dict('os.environ', {
            'SNOWPLOW_API_URL': 'http://localhost:8000',
            'SNOWPLOW_AUTH_MODE': 'sandbox',
            'SNOWPLOW_SANDBOX_TOKEN': 'test-sandbox-token',
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
            assert api_client.auth_mode == "sandbox"
            assert api_client.sandbox_token == "test-sandbox-token"

    @patch('snowplow_signals.batch_autogen.cli.BatchAutogenClient')
    def test_cli_init_with_sandbox_auth_flags(self, mock_client_class):
        """Test CLI init command with SANDBOX auth via command line flags"""
        runner = CliRunner()
        
        # Mock the client
        mock_client = MagicMock()
        mock_client.init_project.return_value = True
        mock_client_class.return_value = mock_client
        
        result = runner.invoke(app, [
            'init',
            '--api-url', 'http://localhost:8000',
            '--auth-mode', 'sandbox',
            '--sandbox-token', 'test-sandbox-token',
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
        assert api_client.auth_mode == "sandbox"
        assert api_client.sandbox_token == "test-sandbox-token"

    @patch('snowplow_signals.batch_autogen.cli.BatchAutogenClient')
    def test_cli_generate_with_sandbox_auth(self, mock_client_class):
        """Test CLI generate command with SANDBOX auth"""
        runner = CliRunner()
        
        # Mock the client
        mock_client = MagicMock()
        mock_client.generate_models.return_value = True
        mock_client_class.return_value = mock_client
        
        result = runner.invoke(app, [
            'generate',
            '--api-url', 'http://localhost:8000',
            '--auth-mode', 'sandbox',
            '--sandbox-token', 'test-sandbox-token',
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
        assert api_client.auth_mode == "sandbox"
        assert api_client.sandbox_token == "test-sandbox-token"


    def test_cli_init_missing_sandbox_token_error(self):
        """Test CLI init command fails when SANDBOX mode is specified but token is missing"""
        runner = CliRunner()
        
        result = runner.invoke(app, [
            'init',
            '--api-url', 'http://localhost:8000',
            '--auth-mode', 'sandbox',
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
