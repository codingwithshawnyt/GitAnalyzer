from pathlib import Path
from datetime import datetime

import pytest

from gitanalyzer.metrics.process.contributors_count import ContributorsCount

# Test data for commit-based analysis
COMMIT_TEST_CASES = [
    # (repository, file_path, start_commit, end_commit, expected_count)
    ('test-repos/gitanalyzer', 
     'gitanalyzer/git_repository.py', 
     'e9854bbea1cb7b7f06cbb559f7b06724d11ae1e5', 
     'e9854bbea1cb7b7f06cbb559f7b06724d11ae1e5', 
     0),
    ('test-repos/gitanalyzer', 
     'gitanalyzer/git_repository.py', 
     'e9854bbea1cb7b7f06cbb559f7b06724d11ae1e5', 
     'ab36bf45859a210b0eae14e17683f31d19eea041', 
     1),
    ('test-repos/gitanalyzer', 
     'gitanalyzer/git_repository.py', 
     '4af3839eb5ea5969f42142529a7a5526739fa570', 
     'ab36bf45859a210b0eae14e17683f31d19eea041', 
     2)
]


@pytest.mark.parametrize('repo_path, file_path, initial_commit, final_commit, expected_result', 
                        COMMIT_TEST_CASES)
def test_minor_contributors_by_commit(repo_path, file_path, initial_commit, 
                                    final_commit, expected_result):
    analyzer = ContributorsCount(
        path_to_repo=repo_path,
        from_commit=initial_commit,
        to_commit=final_commit
    )

    results = analyzer.count_minor()
    normalized_path = str(Path(file_path))
    assert results[normalized_path] == expected_result


# Test data for date-based analysis
DATE_TEST_CASES = [
    # (repository, file_path, start_date, end_date, expected_count)
    ('test-repos/gitanalyzer', 
     'gitanalyzer/git_repository.py', 
     datetime(2018, 8, 1), 
     datetime(2018, 8, 2), 
     0),
    ('test-repos/gitanalyzer', 
     'gitanalyzer/git_repository.py', 
     datetime(2018, 3, 21), 
     datetime(2018, 8, 2), 
     1),
    ('test-repos/gitanalyzer', 
     'gitanalyzer/git_repository.py', 
     datetime(2018, 3, 21), 
     datetime(2019, 1, 14, 10), 
     2)
]


@pytest.mark.parametrize('repo_path, file_path, start_date, end_date, expected_result', 
                        DATE_TEST_CASES)
def test_minor_contributors_by_date(repo_path, file_path, start_date, end_date, 
                                  expected_result):
    analyzer = ContributorsCount(
        path_to_repo=repo_path,
        since=start_date,
        to=end_date
    )

    results = analyzer.count_minor()
    normalized_path = str(Path(file_path))
    assert results[normalized_path] == expected_result