from pathlib import Path
from datetime import datetime

import pytest

from gitanalyzer.metrics.process.hunks_count import HunksCount

# Test data for commit-based analysis
COMMIT_TEST_CASES = [
    {
        'repo_path': 'test-repos/gitanalyzer',
        'file_path': 'scm/git_repository.py',
        'start_commit': '71e053f61fc5d31b3e31eccd9c79df27c31279bf',
        'end_commit': '71e053f61fc5d31b3e31eccd9c79df27c31279bf',
        'expected_hunks': 8
    },
    {
        'repo_path': 'test-repos/gitanalyzer',
        'file_path': 'scm/git_repository.py',
        'start_commit': 'ab36bf45859a210b0eae14e17683f31d19eea041',
        'end_commit': '71e053f61fc5d31b3e31eccd9c79df27c31279bf',
        'expected_hunks': 3
    },
    {
        'repo_path': 'test-repos/gitanalyzer',
        'file_path': 'domain/modification.py',
        'start_commit': 'ab36bf45859a210b0eae14e17683f31d19eea041',
        'end_commit': 'fdf671856b260aca058e6595a96a7a0fba05454b',
        'expected_hunks': 1
    }
]

@pytest.mark.parametrize('test_case', COMMIT_TEST_CASES)
def test_hunk_count_by_commits(test_case):
    analyzer = HunksCount(
        path_to_repo=test_case['repo_path'],
        from_commit=test_case['start_commit'],
        to_commit=test_case['end_commit']
    )
    
    results = analyzer.count()
    normalized_path = str(Path(test_case['file_path']))
    assert results[normalized_path] == test_case['expected_hunks']

# Test data for date-based analysis
DATE_TEST_CASES = [
    {
        'repo_path': 'test-repos/gitanalyzer',
        'file_path': 'scm/git_repository.py',
        'start_date': datetime(2018, 3, 26),
        'end_date': datetime(2018, 3, 27),
        'expected_hunks': 8
    },
    {
        'repo_path': 'test-repos/gitanalyzer',
        'file_path': 'scm/git_repository.py',
        'start_date': datetime(2018, 3, 21),
        'end_date': datetime(2018, 3, 27),
        'expected_hunks': 3
    },
    {
        'repo_path': 'test-repos/gitanalyzer',
        'file_path': 'domain/modification.py',
        'start_date': datetime(2018, 3, 21),
        'end_date': datetime(2018, 3, 22, 23),
        'expected_hunks': 1
    }
]

@pytest.mark.parametrize('test_case', DATE_TEST_CASES)
def test_hunk_count_by_dates(test_case):
    analyzer = HunksCount(
        path_to_repo=test_case['repo_path'],
        since=test_case['start_date'],
        to=test_case['end_date']
    )
    
    results = analyzer.count()
    normalized_path = str(Path(test_case['file_path']))
    assert results[normalized_path] == test_case['expected_hunks']