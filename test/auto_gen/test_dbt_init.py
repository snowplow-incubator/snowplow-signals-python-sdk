"""Tests for the dbt module initialization."""

import importlib
import sys
from unittest.mock import patch, Mock
import pytest


def test_successful_import():
    """Test successful import of the dbt module."""
    # Create a mock DbtClient
    mock_dbt_client = Mock()
    mock_dbt_client.DbtClient = Mock()

    with patch.dict('sys.modules', {
        'snowplow_signals.dbt.dbt_client': mock_dbt_client,
    }):
        # Force reload of the module to apply our mocks
        if 'snowplow_signals.dbt' in sys.modules:
            del sys.modules['snowplow_signals.dbt']
        
        import snowplow_signals.dbt
        
        assert hasattr(snowplow_signals.dbt, 'DbtClient')
        assert snowplow_signals.dbt.__all__ == ['DbtClient'] 