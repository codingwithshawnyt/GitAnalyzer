import logging
from datetime import datetime, timezone, timedelta

from gitanalyzer.repository import Repository

# Configure logging settings
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Define timezone and test timestamps
eastern_timezone = timezone(timedelta(hours=-4))
start_time = datetime(2016, 10, 8, 17, 0, 0, tzinfo=eastern_timezone)
end_time = datetime(2016, 10, 8, 17, 59, 0, tzinfo=eastern_timezone)


def test_commit_range_with_timezone():
    """Test commit retrieval between two dates with timezone information"""
    commits = list(Repository(
        'https://github.com/codingwithshawnyt/GitAnalyzer',
        since=start_time,
        to=end_time
    ).get_commits())

    # Verify expected results
    assert len(commits) == 2
    assert commits[0].commit_id == 'a1b6136f978644ff1d89816bc0f2bd86f6d9d7f5'
    assert commits[1].commit_id == '375de7a8275ecdc0b28dc8de2568f47241f443e9'


def test_commit_range_timezone_naive():
    """Test commit retrieval between two dates without timezone information"""
    local_start = datetime(2016, 10, 8, 21, 0, 0)
    local_end = datetime(2016, 10, 8, 21, 59, 0)
    
    commits = list(Repository(
        'https://github.com/codingwithshawnyt/GitAnalyzer',
        since=local_start,
        to=local_end
    ).get_commits())

    # Validate results
    assert len(commits) == 2
    assert commits[0].commit_id == 'a1b6136f978644ff1d89816bc0f2bd86f6d9d7f5'
    assert commits[1].commit_id == '375de7a8275ecdc0b28dc8de2568f47241f443e9'


def test_commit_range_chronological_reverse():
    """Test commit retrieval in reverse chronological order"""
    commit_history = list(Repository(
        'https://github.com/codingwithshawnyt/GitAnalyzer',
        since=start_time,
        to=end_time,
        sort='reverse'
    ).get_commits())

    # Check reverse order
    assert len(commit_history) == 2
    assert commit_history[0].commit_id == '375de7a8275ecdc0b28dc8de2568f47241f443e9'
    assert commit_history[1].commit_id == 'a1b6136f978644ff1d89816bc0f2bd86f6d9d7f5'
