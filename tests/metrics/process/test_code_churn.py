from pathlib import Path
from datetime import datetime

import pytest

from gitanalyzer.metrics.process.code_churn import CodeChurn

COMMIT_TEST_CASES = [
    (
        'test-repos/gitanalyzer',
        'domain/commit.py',
        'ab36bf45859a210b0eae14e17683f31d19eea041',
        '71e053f61fc5d31b3e31eccd9c79df27c31279bf',
        47,
        34,
        16
    )
]


@pytest.mark.parametrize(
    'repo_path, file_path, initial_commit, final_commit, expected_total, expected_highest, expected_mean',
    COMMIT_TEST_CASES
)
def test_commit_based_analysis(
    repo_path, file_path, initial_commit, final_commit, 
    expected_total, expected_highest, expected_mean
):
    analyzer = CodeChurn(
        path_to_repo=repo_path,
        from_commit=initial_commit,
        to_commit=final_commit
    )

    total_churn = analyzer.count()
    highest_churn = analyzer.max()
    mean_churn = analyzer.avg()

    normalized_path = str(Path(file_path))

    assert total_churn[normalized_path] == expected_total
    assert highest_churn[normalized_path] == expected_highest
    assert mean_churn[normalized_path] == expected_mean


DATE_TEST_CASES = [
    (
        'test-repos/gitanalyzer',
        'domain/commit.py',
        datetime(2018, 3, 21),
        datetime(2018, 3, 27),
        47,
        34,
        16
    )
]


@pytest.mark.parametrize(
    'repo_path, file_path, start_date, end_date, expected_total, expected_highest, expected_mean',
    DATE_TEST_CASES
)
def test_date_based_analysis(
    repo_path, file_path, start_date, end_date,
    expected_total, expected_highest, expected_mean
):
    analyzer = CodeChurn(
        path_to_repo=repo_path,
        since=start_date,
        to=end_date
    )

    total_churn = analyzer.count()
    highest_churn = analyzer.max()
    mean_churn = analyzer.avg()

    normalized_path = str(Path(file_path))

    assert total_churn[normalized_path] == expected_total
    assert highest_churn[normalized_path] == expected_highest
    assert mean_churn[normalized_path] == expected_mean


def test_include_new_files():
    analyzer = CodeChurn(
        path_to_repo='test-repos/gitanalyzer',
        from_commit='ab36bf45859a210b0eae14e17683f31d19eea041',
        to_commit='fdf671856b260aca058e6595a96a7a0fba05454b',
        ignore_added_files=False
    )

    churn_results = analyzer.count()

    assert len(churn_results) == 18
    assert str(Path('domain/__init__.py')) in churn_results
    assert churn_results[str(Path('domain/commit.py'))] == 34


def test_exclude_new_files():
    analyzer = CodeChurn(
        path_to_repo='test-repos/gitanalyzer',
        from_commit='ab36bf45859a210b0eae14e17683f31d19eea041',
        to_commit='fdf671856b260aca058e6595a96a7a0fba05454b',
        ignore_added_files=True
    )

    churn_results = analyzer.count()

    assert len(churn_results) == 7
    assert str(Path('domain/__init__.py')) not in churn_results
    assert churn_results[str(Path('domain/commit.py'))] == 0


def test_include_deletions_in_churn():
    analyzer = CodeChurn(
        path_to_repo='test-repos/gitanalyzer',
        from_commit='ab36bf45859a210b0eae14e17683f31d19eea041',
        to_commit='fdf671856b260aca058e6595a96a7a0fba05454b',
        ignore_added_files=False,
        add_deleted_lines_to_churn=True
    )

    churn_results = analyzer.count()

    assert len(churn_results) == 18
    assert str(Path('domain/__init__.py')) in churn_results
    assert churn_results[str(Path('domain/commit.py'))] == 40


def test_line_change_details():
    analyzer = CodeChurn(
        path_to_repo='test-repos/gitanalyzer',
        from_commit='ab36bf45859a210b0eae14e17683f31d19eea041',
        to_commit='fdf671856b260aca058e6595a96a7a0fba05454b'
    )

    line_changes = analyzer.get_added_and_removed_lines()

    assert isinstance(line_changes, dict)
    assert all(
        isinstance(change_tuple, tuple) and len(change_tuple) == 2 
        for change_tuple in line_changes.values()
    )