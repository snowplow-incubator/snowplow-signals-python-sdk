#!/usr/bin/env python3
import sys
from typing import Literal

VersionType = Literal["patch", "minor", "major"]

def bump_version(current_version: str, version_type: VersionType) -> str:
    """
    Bump the version number based on the specified type.
    
    Args:
        current_version: Current version string (e.g., "1.2.3")
        version_type: Type of version bump ("patch", "minor", or "major")
        
    Returns:
        New version string
    """
    major, minor, patch = map(int, current_version.split("."))
    
    if version_type == "patch":
        patch += 1
    elif version_type == "minor":
        minor += 1
        patch = 0
    elif version_type == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        raise ValueError(f"Invalid version type: {version_type}")
        
    return f"{major}.{minor}.{patch}"

def main():
    if len(sys.argv) != 3:
        print("Usage: python version.py <current_version> <version_type>")
        sys.exit(1)
        
    current_version = sys.argv[1]
    version_type = sys.argv[2]
    
    try:
        new_version = bump_version(current_version, version_type)
        print(new_version)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 