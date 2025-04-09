import json
import sys
from pathlib import Path

def clean_content(content: str) -> str:
    """Clean the content by removing extra whitespace while preserving internal indentation."""
    lines = content.split('\n')
    # Find the minimum indentation (excluding empty lines)
    min_indent = float('inf')
    for line in lines:
        if line.strip():  # Only consider non-empty lines
            indent = len(line) - len(line.lstrip())
            min_indent = min(min_indent, indent)
    
    # Convert to integer for slicing
    min_indent = int(min_indent)
    
    # Remove the minimum indentation from each line and clean up empty lines
    cleaned_lines = []
    for line in lines:
        if line.strip():  # For non-empty lines, remove the minimum indentation
            cleaned_lines.append(line[min_indent:])
        elif cleaned_lines:  # Only keep empty lines if they're not at the start
            cleaned_lines.append('')
    
    # Join the lines and remove any trailing whitespace
    cleaned_content = '\n'.join(cleaned_lines).rstrip()
    
    # Add a single newline at the end if the content is not empty
    return cleaned_content + '\n' if cleaned_content else ''

def replicate_files(snapshot_path: Path, target_dir: Path):
    """Replicate files from a snapshot to a target directory."""
    print(f"Reading snapshot from: {snapshot_path}")
    print(f"Creating files in: {target_dir}")
    
    # Load the snapshot
    try:
        if snapshot_path.suffix == '.ambr':
            # Read the file line by line to preserve formatting
            with open(snapshot_path, 'r') as f:
                content = f.read()
                # Find the start of the dictionary
                dict_start = content.find('dict({')
                if dict_start == -1:
                    raise ValueError("Could not find dictionary in .ambr file")
                
                # Extract the dictionary content
                dict_content = content[dict_start:]
                # Evaluate the dictionary
                snapshot_data = eval(dict_content)
                
                # Process each file
                for file_path, file_content in snapshot_data.items():
                    full_path = target_dir / file_path
                    print(f"Creating: {full_path}")
                    
                    # Create parent directories if they don't exist
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write the file contents
                    try:
                        # Remove the outer triple quotes and clean the content
                        content = file_content.strip("'")
                        cleaned_content = clean_content(content)
                        full_path.write_text(cleaned_content)
                    except Exception as e:
                        print(f"Error writing file {full_path}: {e}")
                        continue
        else:
            # Fallback to JSON for other file types
            snapshot_data = json.loads(snapshot_path.read_text())
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
    
    except FileNotFoundError:
        print(f"Error: Snapshot file not found at {snapshot_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to read snapshot file {snapshot_path}: {e}")
        sys.exit(1)
    
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