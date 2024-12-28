from pathlib import Path
from datetime import datetime

import pytest

from gitanalyzer.metrics.process.lines_count import LinesCount

# Test data for commit-based analysis
COMMIT_TEST_CASES = [
    {
        'repo_path': 'test-repos/gitanalyzer',
        'file_path': '.gitignore',
        'start_commit': 'ab36bf45859a210b0eae14e17683f31d19eea041',
        'end_commit': 'ab36bf45859a210b0eae14e17683f31d19eea041',
        'expected_lines': 197
    },
    {
        'repo_path': 'test-repos/gitanalyzer',
        'file_path': 'domain/modification.py',
        'start_commit': 'ab36bf45859a210b0eae14e17683f31d19eea041',
        'end_commit': '71e053f61fc5d31b3e31eccd9c79df27c31279bf',
        'expected_lines': 65
    }
]

@pytest.mark.parametrize('test_case', COMMIT_TEST_CASES)
def test_line_count_by_commits(test_case):
    # Initialize the line counter
    counter = LinesCount(
        path_to_repo=test_case['repo_path'],
        from_commit=test_case['start_commit'],
        to_commit=test_case['end_commit']
    )
    
    # Get the line count results
    results = counter.count()
    normalized_path = str(Path(test_case['file_path']))
    
    # Verify the results
    assert results[normalized_path] == test_case['expected_lines']

# Test data for date-based analysis
DATE_TEST_CASES = [
    {
        'repo_path': 'test-repos/gitanalyzer',
        'file_path': '.gitignore',
        'start_date': datetime(2018, 3, 21),
        'end_date': datetime(2018, 3, 22),
        'expected_lines': 197
    },
    {
        'repo_path': 'test-repos/gitanalyzer',
        'file_path': 'domain/modification.py',
        'start_date': datetime(2018, 3, 21),
        'end_date': datetime(2018, 3, 27),
        'expected_lines': 65
    }
]

@pytest.mark.parametrize('test_case', DATE_TEST_CASES)
def test_line_count_by_dates(test_case):
    # Initialize the line counter
    counter = LinesCount(
        path_to_repo=test_case['repo_path'],
        since=test_case['start_date'],
        to=test_case['end_date']
    )
    
    # Get the line count results
    results = counter.count()
    normalized_path = str(Path(test_case['file_path']))
    
    # Verify the results
    assert results[normalized_path] == test_case['expected_lines']