import pytest
from datetime import datetime
from gitanalyzer.metrics.process.process_metric import ProcessMetric

# Define test timestamps
timestamp_start = datetime(2016, 10, 8, 17, 0, 0)
timestamp_end = datetime(2016, 10, 8, 17, 59, 0)

# Test scenarios with different parameter combinations
TEST_SCENARIOS = [
    # Scenario 1: Testing without since and from_commit parameters
    (
        'test-repos/gitanalyzer',
        None, 
        timestamp_end,
        None,
        '81ddf7e78d92f3aaa212d5924d1ae0ed1fd980e6'
    ),
    # Scenario 2: Testing without to and to_commit parameters
    (
        'test-repos/gitanalyzer',
        timestamp_start,
        None,
        'ab36bf45859a210b0eae14e17683f31d19eea041',
        None
    )
]

@pytest.mark.parametrize(
    'repository_path, start_date, end_date, initial_commit, final_commit',
    TEST_SCENARIOS
)
def test_invalid_parameter_combination(
    repository_path,
    start_date,
    end_date,
    initial_commit,
    final_commit
):
    """
    Test to verify that invalid parameter combinations raise TypeError.
    """
    with pytest.raises(TypeError):
        ProcessMetric(
            path_to_repo=repository_path,
            since=start_date,
            to=end_date,
            from_commit=initial_commit,
            to_commit=final_commit
        )