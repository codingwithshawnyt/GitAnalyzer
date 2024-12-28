from gitanalyzer import Repository
from gitanalyzer.domain.developer import Developer


REPOSITORY_PATH = "test-repos/contentmine_mailmap"


def test_mailmap_disabled():
    """Test author mapping without .mailmap file"""
    expected_author1 = Developer("Sam Pablo Kuper", "sampablokuper@riseup.net")
    expected_author2 = Developer("My Name", "tarrow@users.noreply.github.com")

    repository = Repository(path_to_repo=REPOSITORY_PATH)
    commit_history = list(repository.traverse_commits())

    # Verify author information matches expected values
    assert commit_history[0].author == expected_author1
    assert commit_history[-1].author == expected_author2


def test_mailmap_enabled():
    """Test author mapping with .mailmap file"""
    expected_author1 = Developer("Sam Pablo Kuper", "sampablokuper@uclmail.net")
    expected_author2 = Developer("Thomas Arrow", "thomasarrow@gmail.com")

    repository = Repository(path_to_repo=REPOSITORY_PATH, use_mailmap=True)
    commit_history = list(repository.traverse_commits())

    # Verify author information is correctly mapped
    assert commit_history[0].author == expected_author1
    assert commit_history[-1].author == expected_author2
