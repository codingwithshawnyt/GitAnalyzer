from pathlib import Path
from datetime import datetime

import pytest

from gitanalyzer.metrics.process.contributors_experience import \
    ContributorsExperience

# Test data for commit-based analysis
COMMIT_TEST_CASES = [
    {
        'repo': 'test-repos/gitanalyzer',
        'file': 'domain/modification.py',
        'start_commit': 'fdf671856b260aca058e6595a96a7a0fba05454b',
        'end_commit': 'ab36bf45859a210b0eae14e17683f31d19eea041',
        'expected_result': 100.0
    },
    {
        'repo': 'test-repos/gitanalyzer',
        'file': 'gitanalyzer/repository_handler.py',
        'start_commit': 'e9854bbea1cb7b7f06cbb559f7b06724d11ae1e5',
        'end_commit': 'e9854bbea1cb7b7f06cbb559f7b06724d11ae1e5',
        'expected_result': 100.0
    },
    {
        'repo': 'test-repos/gitanalyzer',
        'file': 'gitanalyzer/repository_handler.py',
        'start_commit': 'e9854bbea1cb7b7f06cbb559f7b06724d11ae1e5',
        'end_commit': '9d0924301e4fae00eea6d00945bf834455e9a2a6',
        'expected_result': round(100 * 28/30, 2)
    }
]

@pytest.mark.parametrize('test_case', COMMIT_TEST_CASES)
def test_experience_by_commits(test_case):
    """Test contributor experience calculation using commit range."""
    analyzer = ContributorsExperience(
        path_to_repo=test_case['repo'],
        from_commit=test_case['start_commit'],
        to_commit=test_case['end_commit']
    )
    
    results = analyzer.count()
    file_path = str(Path(test_case['file']))
    assert results[file_path] == test_case['expected_result']

# Test data for date-based analysis
DATE_TEST_CASES = [
    {
        'repo': 'test-repos/gitanalyzer',
        'file': 'domain/modification.py',
        'start_date': datetime(2018, 3, 21),
        'end_date': datetime(2018, 3, 23),
        'expected_result': 100.0
    },
    {
        'repo': 'test-repos/gitanalyzer',
        'file': 'gitanalyzer/repository_handler.py',
        'start_date': datetime(2018, 8, 1),
        'end_date': datetime(2018, 8, 2),
        'expected_result': 100.0
    },
    {
        'repo': 'test-repos/gitanalyzer',
        'file': 'gitanalyzer/repository_handler.py',
        'start_date': datetime(2018, 7, 23),
        'end_date': datetime(2018, 8, 2),
        'expected_result': round(100 * 28/30, 2)
    }
]

@pytest.mark.parametrize('test_case', DATE_TEST_CASES)
def test_experience_by_dates(test_case):
    """Test contributor experience calculation using date range."""
    analyzer = ContributorsExperience(
        path_to_repo=test_case['repo'],
        since=test_case['start_date'],
        to=test_case['end_date']
    )
    
    results = analyzer.count()
    file_path = str(Path(test_case['file']))
    assert results[file_path] == test_case['expected_result']