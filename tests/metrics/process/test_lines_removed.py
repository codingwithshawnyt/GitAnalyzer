from pathlib import Path
from datetime import datetime

import pytest

from gitanalyzer.metrics.process.lines_count import LinesCount

# Test data for commit-based analysis
COMMIT_TEST_CASES = [
    {
        'repository': 'test-repos/gitanalyzer',
        'file_path': '.gitignore',
        'start_commit': 'ab36bf45859a210b0eae14e17683f31d19eea041',
        'end_commit': 'ab36bf45859a210b0eae14e17683f31d19eea041',
        'total_lines': 0,
        'maximum_lines': 0,
        'average_lines': 0
    },
    {
        'repository': 'test-repos/gitanalyzer',
        'file_path': 'domain/modification.py',
        'start_commit': 'ab36bf45859a210b0eae14e17683f31d19eea041',
        'end_commit': '71e053f61fc5d31b3e31eccd9c79df27c31279bf',
        'total_lines': 4,
        'maximum_lines': 3,
        'average_lines': 1
    }
]

@pytest.mark.parametrize('test_case', COMMIT_TEST_CASES)
def test_commit_based_analysis(test_case):
    # Initialize the metrics analyzer
    analyzer = LinesCount(
        path_to_repo=test_case['repository'],
        from_commit=test_case['start_commit'],
        to_commit=test_case['end_commit']
    )

    # Calculate metrics
    removed_count = analyzer.count_removed()
    removed_max = analyzer.max_removed()
    removed_avg = analyzer.avg_removed()

    # Normalize file path
    normalized_path = str(Path(test_case['file_path']))

    # Verify results
    assert removed_count[normalized_path] == test_case['total_lines']
    assert removed_max[normalized_path] == test_case['maximum_lines']
    assert removed_avg[normalized_path] == test_case['average_lines']

# Test data for date-based analysis
DATE_TEST_CASES = [
    {
        'repository': 'test-repos/gitanalyzer',
        'file_path': '.gitignore',
        'start_date': datetime(2018, 3, 21),
        'end_date': datetime(2018, 3, 22),
        'total_lines': 0,
        'maximum_lines': 0,
        'average_lines': 0
    },
    {
        'repository': 'test-repos/gitanalyzer',
        'file_path': 'domain/modification.py',
        'start_date': datetime(2018, 3, 21),
        'end_date': datetime(2018, 3, 27),
        'total_lines': 4,
        'maximum_lines': 3,
        'average_lines': 1
    }
]

@pytest.mark.parametrize('test_case', DATE_TEST_CASES)
def test_date_based_analysis(test_case):
    # Initialize the metrics analyzer
    analyzer = LinesCount(
        path_to_repo=test_case['repository'],
        since=test_case['start_date'],
        to=test_case['end_date']
    )

    # Calculate metrics
    removed_count = analyzer.count_removed()
    removed_max = analyzer.max_removed()
    removed_avg = analyzer.avg_removed()

    # Normalize file path
    normalized_path = str(Path(test_case['file_path']))

    # Verify results
    assert removed_count[normalized_path] == test_case['total_lines']
    assert removed_max[normalized_path] == test_case['maximum_lines']
    assert removed_avg[normalized_path] == test_case['average_lines']