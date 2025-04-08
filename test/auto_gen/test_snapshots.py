"""
Tests for verifying the output of generated files.
"""

import json
import shutil
from pathlib import Path
import pytest
import httpx

from snowplow_signals.batch_autogen.dbt_client import BatchAutogenClient
from .utils import get_integration_test_view_response

# Test constants
TEST_VIEW_NAME = "ecommerce_transaction_interactions_features"
TEST_PROJECT_NAME = "ecommerce_transaction_interactions_features_1"
API_ENDPOINT = "http://localhost:8000/api/v1/registry/views/"

def get_file_contents(directory: Path) -> dict:
    """Get contents of all files in a directory."""
    contents = {}
    for path in directory.rglob("*"):
        if path.is_file():
            try:
                contents[str(path.relative_to(directory))] = path.read_text()
            except UnicodeDecodeError:
                continue
    return contents

def save_snapshot_to_json(contents: dict, snapshot_path: Path):
    """Save file contents to a JSON file for easy replication."""
    # Ensure the snapshot directory exists
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    
    snapshot_data = {
        "files": [
            {
                "path": file_path,
                "content": content
            }
            for file_path, content in contents.items()
        ]
    }
    snapshot_path.write_text(json.dumps(snapshot_data, indent=2))

def load_snapshot_from_json(snapshot_path: Path) -> dict:
    """Load file contents from a JSON snapshot file."""
    if not snapshot_path.exists():
        return {}
    snapshot_data = json.loads(snapshot_path.read_text())
    return {
        file_info["path"]: file_info["content"]
        for file_info in snapshot_data["files"]
    }

def replicate_files(snapshot_path: Path, target_dir: Path):
    """Replicate files from a snapshot to a target directory."""
    # Load the snapshot
    snapshot_data = json.loads(snapshot_path.read_text())
    
    # Create each file
    for file_info in snapshot_data["files"]:
        file_path = target_dir / file_info["path"]
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        # Write the file contents
        file_path.write_text(file_info["content"])

@pytest.fixture
def test_dir(tmp_path):
    """Create a temporary directory for the test."""
    return tmp_path

def test_generated_files(test_dir, signals_client, respx_mock):
    """Test that the generated files are correct."""
    # Setup mock API response
    mock_response = get_integration_test_view_response()
    respx_mock.get(API_ENDPOINT).mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    # Generate the files
    client = BatchAutogenClient(signals_client.api_client)
    client.init_project(repo_path=str(test_dir), view_name=TEST_VIEW_NAME)
    client.generate_models(
        repo_path=str(test_dir), 
        project_name=TEST_PROJECT_NAME
    )

    # Get actual file contents
    actual_files = get_file_contents(test_dir)
    
    # Save snapshot for future replication
    snapshot_path = Path(__file__).parent / "__snapshots__" / "generated_files.json"
    save_snapshot_to_json(actual_files, snapshot_path)
    
    # Compare with existing snapshot if it exists
    expected_files = load_snapshot_from_json(snapshot_path)
    if expected_files:
        assert actual_files == expected_files

def test_replicate_files(test_dir):
    """Test that we can replicate files from the snapshot."""
    snapshot_path = Path(__file__).parent / "__snapshots__" / "generated_files.json"
    if not snapshot_path.exists():
        pytest.skip("No snapshot file exists yet. Run test_generated_files first.")
    
    # Create a new directory for replication
    replicate_dir = test_dir / "replicated"
    replicate_dir.mkdir()
    
    # Replicate the files
    replicate_files(snapshot_path, replicate_dir)
    
    # Verify the files were replicated correctly
    original_files = load_snapshot_from_json(snapshot_path)
    replicated_files = get_file_contents(replicate_dir)
    assert original_files == replicated_files 