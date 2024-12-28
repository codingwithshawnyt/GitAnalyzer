from pathlib import Path
from datetime import datetime

import pytest

from gitanalyzer.metrics.process.commits_count import CommitsCount

# Test data for commit-based analysis
COMMIT_TEST_CASES = [
    (
        'test-repos/gitanalyzer',
        'domain/developer.py',
        'fdf671856b260aca058e6595a96a7a0fba05454b',
        'ab36bf45859a210b0eae14e17683f31d19eea041',
        2
    ),
    (
        'test-repos/gitanalyzer',
        'domain/developer.py',
        'ab36bf45859a210b0eae14e17683f31d19eea041',
        'fdf671856b260aca058e6595a96a7a0fba05454b',
        2
    )
]

@pytest.mark.parametrize(
    'repository_path, file_path, start_commit, end_commit, expected_count',
    COMMIT_TEST_CASES
)
def test_commit_based_count(repository_path, file_path, start_commit, end_commit, expected_count):
    """
    Verify commit counting functionality using commit hashes as boundaries
    """
    analyzer = CommitsCount(
        path_to_repo=repository_path,
        from_commit=start_commit,
        to_commit=end_commit
    )
    
    results = analyzer.count()
    normalized_path = str(Path(file_path))
    assert results[normalized_path] == expected_count

# Test data for date-based analysis
DATE_TEST_CASES = [
    (
        'test-repos/gitanalyzer',
        'domain/developer.py',
        datetime(2018, 3, 21),
        datetime(2018, 3, 23),
        2
    )
]

@pytest.mark.parametrize(
    'repository_path, file_path, start_date, end_date, expected_count',
    DATE_TEST_CASES
)
def test_date_based_count(repository_path, file_path, start_date, end_date, expected_count):
    """
    Verify commit counting functionality using dates as boundaries
    """
    analyzer = CommitsCount(
        path_to_repo=repository_path,
        since=start_date,
        to=end_date
    )
    
    results = analyzer.count()
    normalized_path = str(Path(file_path))
    assert results[normalized_path] == expected_count