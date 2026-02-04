#!/usr/bin/env python3
import sys
import semver
import re
from typing import Literal

VersionType = Literal["patch", "minor", "major"]
PrereleaseType = Literal["rc", "alpha", "beta"]


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


def bump_prerelease(
    current_version: str,
    prerelease_type: PrereleaseType,
    version_bump: VersionType = "patch",
) -> str:
    """
    Bump to a pre-release version.

    If current version is stable (e.g., "1.2.3"), bumps to next version with pre-release.
    If current version is already a pre-release, increments the pre-release number
    (or changes the pre-release type if different).

    Args:
        current_version: Current version string (e.g., "1.2.3" or "1.2.4-rc1")
        prerelease_type: Type of pre-release ("rc", "alpha", "beta")
        version_bump: Version component to bump if starting from stable ("patch", "minor", "major")

    Returns:
        New pre-release version string (format: X.Y.Z-rc1)
    """
    version = semver.VersionInfo.parse(current_version)

    # If already a pre-release
    if version.prerelease:
        match = re.match(r"([a-z]+)(\d+)", version.prerelease)
        if match:
            prefix, num = match.groups()
            # If changing pre-release type, start at 1
            if prefix != prerelease_type:
                new_prerelease = f"{prerelease_type}1"
            else:
                # Same type, increment the number
                new_prerelease = f"{prefix}{int(num) + 1}"
        else:
            raise ValueError("Invalid pre-release format")

        new_version = version.replace(prerelease=new_prerelease)
    else:
        # Bump to next version with pre-release identifier
        if version_bump == "patch":
            new_version = version.bump_patch()
        elif version_bump == "minor":
            new_version = version.bump_minor()
        elif version_bump == "major":
            new_version = version.bump_major()
        else:
            raise ValueError(f"Invalid version type: {version_bump}")

        # Add pre-release identifier
        new_version = new_version.replace(prerelease=f"{prerelease_type}1")

    return str(new_version)


def finalize_version(current_version: str) -> str:
    """
    Finalize a pre-release version by stripping the pre-release suffix.

    Args:
        current_version: Current version string (e.g., "1.2.3-rc1")

    Returns:
        Finalized version string (e.g., "1.2.3")

    Raises:
        ValueError: If current version is not a pre-release
    """
    version = semver.VersionInfo.parse(current_version)

    if not version.prerelease:
        raise ValueError(f"Version {current_version} is not a pre-release")

    return f"{version.major}.{version.minor}.{version.patch}"


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: python version.py <current_version> <version_type> [prerelease_type]"
        )
        print("  version_type: patch, minor, major, finalize")
        print("  prerelease_type (optional): rc, alpha, beta")
        sys.exit(1)

    current_version = sys.argv[1]
    version_type_str = sys.argv[2]
    prerelease_type_str = sys.argv[3] if len(sys.argv) > 3 else None

    try:
        if version_type_str == "finalize":
            new_version = finalize_version(current_version)
        elif prerelease_type_str:
            if version_type_str not in ("patch", "minor", "major"):
                raise ValueError(
                    f"Invalid version type: {version_type_str}. Must be one of: patch, minor, major"
                )
            if prerelease_type_str not in ("rc", "alpha", "beta"):
                raise ValueError(
                    f"Invalid prerelease type: {prerelease_type_str}. Must be one of: rc, alpha, beta"
                )
            version_type: VersionType = version_type_str  # type: ignore
            prerelease_type: PrereleaseType = prerelease_type_str  # type: ignore
            new_version = bump_prerelease(
                current_version, prerelease_type, version_type
            )
        else:
            if version_type_str not in ("patch", "minor", "major"):
                raise ValueError(
                    f"Invalid version type: {version_type_str}. Must be one of: patch, minor, major"
                )
            version_type: VersionType = version_type_str  # type: ignore
            new_version = bump_version(current_version, version_type)

        print(new_version)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
