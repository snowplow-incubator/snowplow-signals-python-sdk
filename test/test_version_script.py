import os
import sys

import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
)

from version import (  # noqa: E402
    bump_prerelease,
    bump_version,
    normalize_to_semver,
)


class TestNormalizeToSemver:
    @pytest.mark.parametrize(
        "pep440,expected",
        [
            ("0.4.7rc1", "0.4.7-rc1"),
            ("0.5.0beta2", "0.5.0-beta2"),
            ("1.0.0alpha1", "1.0.0-alpha1"),
        ],
    )
    def test_inserts_hyphen_for_pep440_prerelease(self, pep440, expected):
        assert normalize_to_semver(pep440) == expected

    @pytest.mark.parametrize(
        "version",
        ["0.4.7-rc1", "0.5.0-beta2", "1.0.0", "2.3.4"],
    )
    def test_is_idempotent_for_semver_and_stable(self, version):
        assert normalize_to_semver(version) == version


class TestBumpPrerelease:
    def test_increments_from_pep440_prerelease(self):
        # Regression: Poetry writes "0.4.7rc1"; must not raise "not valid SemVer".
        assert bump_prerelease("0.4.7rc1", "rc") == "0.4.7-rc2"

    def test_increments_from_semver_prerelease(self):
        assert bump_prerelease("0.4.7-rc1", "rc") == "0.4.7-rc2"

    def test_starts_prerelease_from_stable(self):
        assert bump_prerelease("0.4.6", "rc") == "0.4.7-rc1"

    def test_respects_version_bump_from_stable(self):
        assert bump_prerelease("0.4.6", "beta", "minor") == "0.5.0-beta1"


class TestBumpVersion:
    def test_bump_from_pep440_prerelease(self):
        assert bump_version("0.4.7rc1", "patch") == "0.4.8"

    def test_bump_patch_from_stable(self):
        assert bump_version("0.4.6", "patch") == "0.4.7"
