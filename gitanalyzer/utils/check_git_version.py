from subprocess import run, PIPE
import re


class GitVersionError(Exception):
    """Custom exception for Git version compatibility issues."""
    pass


def validate_git_installation():
    """
    Validates if the installed Git version meets the minimum requirement (2.38).
    
    Raises:
        GitVersionError: If Git version is below 2.38
    """
    try:
        # Execute git version command and capture output
        result = run(["git", "--version"], stdout=PIPE, text=True)
        version_string = result.stdout.strip()
        
        # Extract version number using regex
        match = re.search(r"(\d+\.\d+)", version_string)
        if not match:
            raise GitVersionError("Unable to determine Git version")
            
        installed_version = float(match.group(1))
        MINIMUM_VERSION = 2.38
        
        if installed_version < MINIMUM_VERSION:
            raise GitVersionError(
                f"Git version {installed_version} is not supported. "
                f"Please upgrade to version {MINIMUM_VERSION} or higher."
            )
            
    except FileNotFoundError:
        raise GitVersionError("Git is not installed or not found in system PATH")
