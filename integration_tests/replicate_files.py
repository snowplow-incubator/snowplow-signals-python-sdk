import json
import sys
from pathlib import Path

def replicate_files(snapshot_path: Path, target_dir: Path):
    """Replicate files from a snapshot to a target directory."""
    print(f"Reading snapshot from: {snapshot_path}")
    print(f"Creating files in: {target_dir}")
    
    # Load the snapshot
    try:
        snapshot_data = json.loads(snapshot_path.read_text())
    except FileNotFoundError:
        print(f"Error: Snapshot file not found at {snapshot_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in snapshot file {snapshot_path}")
        sys.exit(1)
    
    # Create target directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Create each file
    for file_info in snapshot_data["files"]:
        file_path = target_dir / file_info["path"]
        print(f"Creating: {file_path}")
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file contents
        try:
            file_path.write_text(file_info["content"])
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")
            continue
    
    print("\nDone! Files have been replicated successfully.")

def main():
    if len(sys.argv) != 3:
        print("Usage: python replicate_files.py <snapshot_path> <target_dir>")
        sys.exit(1)
    
    snapshot_path = Path(sys.argv[1])
    target_dir = Path(sys.argv[2])
    
    replicate_files(snapshot_path, target_dir)

if __name__ == "__main__":
    main() 