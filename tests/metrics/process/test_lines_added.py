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
        'total_lines': 197,
        'max_lines': 197,
        'avg_lines': 197
    },
    {
        'repo_path': 'test-repos/gitanalyzer',
        'file_path': 'domain/modification.py',
        'start_commit': 'ab36bf45859a210b0eae14e17683f31d19eea041',
        'end_commit': '71e053f61fc5d31b3e31eccd9c79df27c31279bf',
        'total_lines': 61,
        'max_lines': 48,
        'avg_lines': 20
    }
]

@pytest.mark.parametrize('test_case', COMMIT_TEST_CASES)
def test_commit_based_analysis(test_case):
    """Test line counting functionality using commit hashes."""
    analyzer = LinesCount(
        path_to_repo=test_case['repo_path'],
        from_commit=test_case['start_commit'],
        to_commit=test_case['end_commit']
    )

    file_path = str(Path(test_case['file_path']))
    
    # Calculate metrics
    total_added = analyzer.count_added()
    maximum_added = analyzer.max_added()
    average_added = analyzer.avg_added()

    # Verify results
    assert total_added[file_path] == test_case['total_lines']
    assert maximum_added[file_path] == test_case['max_lines']
    assert average_added[file_path] == test_case['avg_lines']

# Test data for date-based analysis
DATE_TEST_CASES = [
    {
        'repo_path': 'test-repos/gitanalyzer',
        'file_path': '.gitignore',
        'start_date': datetime(2018, 3, 21),
        'end_date': datetime(2018, 3, 22),
        'total_lines': 197,
        'max_lines': 197,
        'avg_lines': 197
    },
    {
        'repo_path': 'test-repos/gitanalyzer',
        'file_path': 'domain/modification.py',
        'start_date': datetime(2018, 3, 21),
        'end_date': datetime(2018, 3, 27),
        'total_lines': 61,
        'max_lines': 48,
        'avg_lines': 20
    }
]

@pytest.mark.parametrize('test_case', DATE_TEST_CASES)
def test_date_based_analysis(test_case):
    """Test line counting functionality using date ranges."""
    analyzer = LinesCount(
        path_to_repo=test_case['repo_path'],
        since=test_case['start_date'],
        to=test_case['end_date']
    )

    file_path = str(Path(test_case['file_path']))
    
    # Calculate metrics
    total_added = analyzer.count_added()
    maximum_added = analyzer.max_added()
    average_added = analyzer.avg_added()

    # Verify results
    assert total_added[file_path] == test_case['total_lines']
    assert maximum_added[file_path] == test_case['max_lines']
    assert average_added[file_path] == test_case['avg_lines']