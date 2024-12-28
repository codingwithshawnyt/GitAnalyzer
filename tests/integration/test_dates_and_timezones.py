import logging
from datetime import datetime, timezone, timedelta
from gitanalyzer.repository import Repository

# Configure logging with timestamp and level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def test_timezone_positive_offset():
    """
    Test commit dates with a positive timezone offset
    """
    # Initialize repository with specific commit
    repo = Repository(
        path='https://github.com/codingwithshawnyt/GitAnalyzer',
        commit_hash='29e929fbc5dc6a2e9c620069b24e2a143af4285f'
    )
    
    # Get all commits
    commits = repo.traverse_commits()
    first_commit = list(commits)[0]
    
    # Create expected datetime (UTC+2)
    expected_time = datetime(
        year=2016,
        month=4,
        day=4,
        hour=13,
        minute=21,
        second=25,
        tzinfo=timezone(timedelta(hours=2))
    )
    
    # Verify commit date matches expected
    assert first_commit.author_date == expected_time


def test_timezone_negative_offset():
    """
    Test commit dates with a negative timezone offset
    """
    # Initialize repository with specific commit
    repo = Repository(
        path='https://github.com/codingwithshawnyt/GitAnalyzer',
        commit_hash='375de7a8275ecdc0b28dc8de2568f47241f443e9'
    )
    
    # Get all commits
    commits = repo.traverse_commits()
    first_commit = list(commits)[0]
    
    # Create expected datetime (UTC-4)
    expected_time = datetime(
        year=2016,
        month=10,
        day=8,
        hour=17,
        minute=57,
        second=49,
        tzinfo=timezone(timedelta(hours=-4))
    )
    
    # Verify commit date matches expected
    assert first_commit.author_date == expected_time
