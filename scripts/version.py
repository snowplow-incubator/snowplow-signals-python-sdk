#!/usr/bin/env python3
import sys
import semver
from typing import Literal

VersionType = Literal["patch", "minor", "major"]

def bump_version(current_version: str, version_type: VersionType) -> str:
    """
    Bump the version number based on the specified type using semver.
    
    Args:
        current_version: Current version string (e.g., "1.2.3")
        version_type: Type of version bump ("patch", "minor", or "major")
        
    Returns:
        New version string
    """
    version = semver.VersionInfo.parse(current_version)
    
    if version_type == "patch":
        new_version = version.bump_patch()
    elif version_type == "minor":
        new_version = version.bump_minor()
    elif version_type == "major":
        new_version = version.bump_major()
    else:
        raise ValueError(f"Invalid version type: {version_type}")
        
    return str(new_version)

def main():
    if len(sys.argv) != 3:
        print("Usage: python version.py <current_version> <version_type>")
        sys.exit(1)
        
    current_version = sys.argv[1]
    version_type_str = sys.argv[2]
    
    try:
        if version_type_str not in ("patch", "minor", "major"):
            raise ValueError(f"Invalid version type: {version_type_str}. Must be one of: patch, minor, major")
        version_type: VersionType = version_type_str  # type: ignore
        new_version = bump_version(current_version, version_type)
        print(new_version)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 