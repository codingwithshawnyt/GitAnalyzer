import pytest
from datetime import datetime
from gitanalyzer.metrics.process.change_set import ChangeSet

# Test data for commit-based analysis
COMMIT_TEST_CASES = [
    (
        'test-repos/gitanalyzer',
        'ab36bf45859a210b0eae14e17683f31d19eea041',
        '71e053f61fc5d31b3e31eccd9c79df27c31279bf',
        13,  # expected maximum
        8    # expected average
    )
]

def verify_changeset_metrics(changeset, expected_maximum, expected_average):
    """Helper function to verify changeset metrics"""
    computed_max = changeset.max()
    computed_avg = changeset.avg()
    
    assert computed_max == expected_maximum
    assert computed_avg == expected_average

@pytest.mark.parametrize(
    'repository_path, start_commit, end_commit, max_expected, avg_expected',
    COMMIT_TEST_CASES
)
def test_changeset_commit_analysis(
    repository_path, start_commit, end_commit, max_expected, avg_expected
):
    analyzer = ChangeSet(
        path_to_repo=repository_path,
        from_commit=start_commit,
        to_commit=end_commit
    )
    
    verify_changeset_metrics(analyzer, max_expected, avg_expected)

# Test data for date-based analysis
DATE_TEST_CASES = [
    (
        'test-repos/gitanalyzer',
        datetime(2018, 3, 21),
        datetime(2018, 3, 27),
        13,  # expected maximum
        8    # expected average
    ),
    (
        'test-repos/gitanalyzer',
        datetime(2018, 3, 23),
        datetime(2018, 3, 23),
        0,   # expected maximum
        0    # expected average
    )
]

@pytest.mark.parametrize(
    'repository_path, start_date, end_date, max_expected, avg_expected',
    DATE_TEST_CASES
)
def test_changeset_date_analysis(
    repository_path, start_date, end_date, max_expected, avg_expected
):
    analyzer = ChangeSet(
        path_to_repo=repository_path,
        since=start_date,
        to=end_date
    )
    
    verify_changeset_metrics(analyzer, max_expected, avg_expected)