import pytest
from unittest.mock import patch
from contextlib import nullcontext as no_error_expected
from gitanalyzer.utils.check_git_version import GitVersionChecker, GitVersionError


class TestGitVersionValidation:
    @pytest.mark.parametrize(
        "git_version,expected_outcome",
        [
            ("3.2.0", no_error_expected()),
            ("2.38.1", no_error_expected()),
            ("2.0.0", pytest.raises(GitVersionError)),
        ],
    )
    def test_git_version_validation(self, git_version, expected_outcome):
        """
        Verify that the git version checker correctly validates different git versions.
        Tests both valid and invalid git versions.
        """
        with patch(
            "gitanalyzer.utils.check_git_version.subprocess.check_output"
        ) as mocked_version:
            # Configure mock to return specific git version
            mocked_version.return_value.decode.return_value.strip.return_value = (
                f"git version {git_version}"
            )
            
            # Verify version check behavior
            with expected_outcome:
                GitVersionChecker().validate_git_version()