from pathlib import Path
from datetime import datetime

import pytest

from gitanalyzer.metrics.process.contributors_count import ContributorsCount

# Test data for commit-based analysis
COMMIT_TEST_CASES = [
    (
        'test-repos/gitanalyzer',
        'gitanalyzer/repository_handler.py',
        '8b69cae085581256adfdbd58c0e499395819b84d',
        '115953109b57d841ccd0952d70f8ed6703d175cd',
        2
    ),
    (
        'test-repos/gitanalyzer',
        'domain/change.py',
        '71e053f61fc5d31b3e31eccd9c79df27c31279bf',
        'ab36bf45859a210b0eae14e17683f31d19eea041',
        1
    )
]


@pytest.mark.parametrize(
    'repo_path, file_path, start_commit, end_commit, expected_count',
    COMMIT_TEST_CASES
)
def test_contributor_count_by_commits(
    repo_path, file_path, start_commit, end_commit, expected_count
):
    analyzer = ContributorsCount(
        path_to_repo=repo_path,
        from_commit=start_commit,
        to_commit=end_commit
    )

    result = analyzer.count()
    normalized_path = str(Path(file_path))
    assert result[normalized_path] == expected_count


# Test data for date-based analysis
DATE_TEST_CASES = [
    (
        'test-repos/gitanalyzer',
        'gitanalyzer/repository_handler.py',
        datetime(2019, 12, 17),
        datetime(2019, 12, 24),
        2
    ),
    (
        'test-repos/gitanalyzer',
        'domain/change.py',
        datetime(2018, 3, 21),
        datetime(2018, 3, 27),
        1
    )
]


@pytest.mark.parametrize(
    'repo_path, file_path, start_date, end_date, expected_count',
    DATE_TEST_CASES
)
def test_contributor_count_by_dates(
    repo_path, file_path, start_date, end_date, expected_count
):
    analyzer = ContributorsCount(
        path_to_repo=repo_path,
        since=start_date,
        to=end_date
    )

    result = analyzer.count()
    normalized_path = str(Path(file_path))
    assert result[normalized_path] == expected_count