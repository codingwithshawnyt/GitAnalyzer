import logging
import pytest

from gitanalyzer.repository import Repository
from gitanalyzer.commit_analysis import Commit, DMMProperty

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

@pytest.fixture()
def repository():
    repo_path = "https://github.com/codingwithshawnyt/GitAnalyzer"
    repo = Repository(repo_path)
    yield repo
    repo.cleanup()

# Define test data for unit size DMM calculations
UNIT_SIZE_TESTS = [
    ('Commit with one large method', 0.0),
    ('Make large larger, add small method', 0.8),
    ('Make large larger, make small smaller', 0.0),
    ('Modify every line in large method', None),
    ('Make small method a bit larger', 1.0),
    ('Make small smaller', 0.0),
    ('Make large smaller, make small smaller', 2/3),
    ('Make large smaller', 1.0),
    ('Make large smaller, make small larger', 1.0),
    ('Increase in one, decrease in other file', 3/4),
    ('Add method with unit size on-point', 1.0),
    ('Increase unit size to risky', 0.0)
]

UNIT_COMPLEXITY_TESTS = [
    ('Commit with one large method', 1.0),
    ('Add method with complexity on-point', 1.0),
    ('Increase complexity to risky', 0.0)
]

UNIT_INTERFACING_TESTS = [
    ('Commit with one large method', 1.0),
    ('Add method with interfacing on-point', None),
    ('Increase interfacing to risky', 0.0)
]

def find_commit_by_message(repository: Repository, message: str) -> Commit:
    for commit in repository.list_commits():
        if commit.message == message:
            return commit
    raise ValueError('Commit with message "{}" not found'.format(message))

@pytest.mark.parametrize('message,dmm', UNIT_SIZE_TESTS)
def test_unit_size_dmm(repository: Repository, message: str, dmm: float):
    commit = find_commit_by_message(repository, message)
    assert commit.dmm_unit_size == dmm

@pytest.mark.parametrize('message,dmm', UNIT_COMPLEXITY_TESTS)
def test_unit_complexity_dmm(repository: Repository, message: str, dmm: float):
    commit = find_commit_by_message(repository, message)
    assert commit.dmm_unit_complexity == dmm

@pytest.mark.parametrize('message,dmm', UNIT_INTERFACING_TESTS)
def test_unit_interfacing_dmm(repository: Repository, message: str, dmm: float):
    commit = find_commit_by_message(repository, message)
    assert commit.dmm_unit_interfacing == dmm

def test_language_not_supported(repository: Repository):
    commit = find_commit_by_message(repository, 'Offer README explaining the repo purpose')
    assert commit.dmm_unit_size is None

def test_mixed_language_support(repository: Repository):
    commit = find_commit_by_message(repository, 'Release under Apache 2 license')
    assert commit.dmm_unit_size is None

def test_change_in_delta_profile(repository: Repository):
    commit = find_commit_by_message(repository, 'Increase unit size to risky')
    modified_file = commit.modified_files[0]
    assert modified_file.delta_risk_profile(DMMProperty.UNIT_SIZE) == (-15, 16)

def test_commit_delta_profile(repository: Repository):
    commit = find_commit_by_message(repository, 'Increase in one, decrease in other file')
    file1 = commit.modified_files[0]
    assert file1.delta_risk_profile(DMMProperty.UNIT_SIZE) == (0, 1)
    file2 = commit.modified_files[1]
    assert file2.delta_risk_profile(DMMProperty.UNIT_SIZE) == (3, 0)
    assert commit.delta_risk_profile(DMMProperty.UNIT_SIZE) == (3, 1)

def test_supported_file_types(repository: Repository):
    commit = find_commit_by_message(repository, 'Offer README explaining the repo purpose')
    modified_file = commit.modified_files[0]
    assert not modified_file.is_language_supported

@pytest.mark.parametrize(
    'delta_low,delta_high,property', [
        (0,  0, None),
        (1,  0, 1.0),
        (-1,  0, 0.0),
        (0,  1, 0.0),
        (0, -1, 1.0),
        (1,  1, 0.5),
        (-1, -1, 0.5),
        (1, -1, 1.0),
        (-1,  1, 0.0)
    ])
def test_proper_change_ratio(delta_low: int, delta_high: int, property: float):
    assert Commit.calculate_good_change_proportion(delta_low, delta_high) == property