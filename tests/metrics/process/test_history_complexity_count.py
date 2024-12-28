from pathlib import Path
from datetime import datetime

import pytest
from gitanalyzer.metrics.process.history_complexity import HistoryComplexity

# Test data for commit-based tests
COMMIT_TEST_CASES = [
    {
        'repository': 'test-repos/gitanalyzer',
        'file_path': 'scm/git_repository.py',
        'initial_commit': '90ca34ebfe69629cb7f186a1582fc38a73cc572e',
        'final_commit': '90ca34ebfe69629cb7f186a1582fc38a73cc572e',
        'expected_value': 40.49
    },
    {
        'repository': 'test-repos/gitanalyzer',
        'file_path': 'scm/git_repository.py',
        'initial_commit': '71e053f61fc5d31b3e31eccd9c79df27c31279bf',
        'final_commit': '90ca34ebfe69629cb7f186a1582fc38a73cc572e',
        'expected_value': 47.05
    },
    {
        'repository': 'https://github.com/codingwithshawnyt/GitAnalyzer',
        'file_path': 'tasks/main.yml',
        'initial_commit': '7fb350c30be1124b51aab4a88352428e0a853b9a',
        'final_commit': '678429591513fe86045e892a1da680c8ac36e00f',
        'expected_value': 0.0
    }
]

@pytest.mark.parametrize('test_case', COMMIT_TEST_CASES)
def test_complexity_with_commit_range(test_case):
    analyzer = HistoryComplexity(
        path_to_repo=test_case['repository'],
        from_commit=test_case['initial_commit'],
        to_commit=test_case['final_commit']
    )
    
    result = analyzer.count()
    normalized_path = str(Path(test_case['file_path']))
    assert result[normalized_path] == test_case['expected_value']

# Test data for date-based tests
DATE_TEST_CASES = [
    {
        'repository': 'test-repos/gitanalyzer',
        'file_path': 'scm/git_repository.py',
        'start_date': datetime(2018, 3, 22, 11, 30),
        'end_date': datetime(2018, 3, 23),
        'expected_value': 40.49
    },
    {
        'repository': 'test-repos/gitanalyzer',
        'file_path': 'scm/git_repository.py',
        'start_date': datetime(2018, 3, 22, 11, 30),
        'end_date': datetime(2018, 3, 27),
        'expected_value': 47.05
    }
]

@pytest.mark.parametrize('test_case', DATE_TEST_CASES)
def test_complexity_with_date_range(test_case):
    analyzer = HistoryComplexity(
        path_to_repo=test_case['repository'],
        since=test_case['start_date'],
        to=test_case['end_date']
    )
    
    result = analyzer.count()
    normalized_path = str(Path(test_case['file_path']))
    assert result[normalized_path] == test_case['expected_value']