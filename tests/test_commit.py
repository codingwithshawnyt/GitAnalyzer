from gitanalyzer.repository import Repository
from pathlib import Path
from unittest.mock import patch
import pytest
import logging

from gitanalyzer.domain.modification import ModifiedSourceFile

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


@pytest.fixture
def repository(request):
    repo = Repository(request.param)
    yield repo
    repo.cleanup()


@pytest.mark.parametrize('repository', ['test-repos/complex_repo'], indirect=True)
def test_comparisons(repository: Repository):
    commit1 = repository.get_commit('e7d13b0511f8a176284ce4f92ed8c6e8d09c77f2')
    commit2 = repository.get_commit(commit1.parents[0])
    commit3 = repository.get_commit('a4ece0762e797d2e2dcbd471115108dd6e05ff58')

    assert commit1.parents[0] == 'a4ece0762e797d2e2dcbd471115108dd6e05ff58'
    assert commit3 == commit2
    assert commit1 != commit3


@patch('git.diff.Diff')
def test_file_names(mock_diff):
    mock_diff.a_path = 'codingwithshawnyt/GitAnalyzer/myfile.py'
    mock_diff.b_path = 'codingwithshawnyt/GitAnalyzer/mynewfile.py'

    modified_file = ModifiedSourceFile(mock_diff)

    assert modified_file.filename == 'mynewfile.py'

    assert modified_file.new_path == str(Path('codingwithshawnyt/GitAnalyzer/mynewfile.py'))
    assert modified_file.old_path == str(Path('codingwithshawnyt/GitAnalyzer/myfile.py'))


@patch('git.diff.Diff')
def test_python_metrics(mock_diff):
    with open('test-repos/lizard/git_repository.py', 'rb') as file:
        file_content = file.read()

    mock_diff.a_path = 'test-repos/lizard/git_repository.py'
    mock_diff.b_path = "test-repos/lizard/git_repository.py"
    mock_diff.b_blob.data_stream.read.return_value = file_content

    modified_file = ModifiedSourceFile(mock_diff)

    assert modified_file.nloc == 196
    assert modified_file.token_count == 1009
    assert modified_file.complexity == 43

    assert len(modified_file.methods) == 19


def test_method_changes():

    repo = Repository("test-repos/diff")

    # add a new method
    modification = repo.get_commit(
        'ea95227e0fd128aa69c7ab6a8ac485f72251b3ed').modified_files[0]
    assert len(modification.changed_methods) == 1
    assert modification.changed_methods[0].name == 'GitRepository::singleProjectThirdMethod'

    # add 2 new methods
    modification = repo.get_commit(
        'd8eb8e80b671246a43c98d97b05f6d1c5ada14fb').modified_files[0]
    assert len(modification.changed_methods) == 2

    # remove one method
    modification = repo.get_commit(
        '0c8f9fdec926785198b399a2c49adb5884aa952c').modified_files[0]
    assert len(modification.changed_methods) == 1

    # add and remove one one method at different locations
    modification = repo.get_commit(
        'd8bb142c5616041b71cbfaa11eeb768d9a1a296e').modified_files[0]
    assert len(modification.changed_methods) == 2

    # add and remove one one method at the same location
    # this is equivalent to replacing a method - although we expect 2 methods
    modification = repo.get_commit(
        '9e9473d5ca310b7663e9df93c402302b6b7f24aa').modified_files[0]
    assert len(modification.changed_methods) == 2

    # update a method
    modification = repo.get_commit(
        'b267a14e0503fdac36d280422f16360d1f661f12').modified_files[0]
    assert len(modification.changed_methods) == 1

    # update and add a new method
    modification = repo.get_commit(
        '2489099dfd90edb99ddc2c82b62524b66c07c687').modified_files[0]
    assert len(modification.changed_methods) == 2

    # update and delete methods
    modification = repo.get_commit(
        '5aebeb30e0238543a93e5bed806639481460cd9a').modified_files[0]
    assert len(modification.changed_methods) == 2

    # delete 3 methods (test cleanup - revert the test file to its
    # initial set of methods)
    modification = repo.get_commit(
        '9f6ddc2aac740a257af59a76860590cb8a84c77b').modified_files[0]
    assert len(modification.changed_methods) == 3


@pytest.mark.parametrize('repo', ['test-repos/small_repo'], indirect=True)
def test_timezone_offset_plus_hours(repo: Repository):
    timezone1 = repo.get_commit('da39b1326dbc2edfe518b90672734a08f3c13458').author_timezone
    timezone2 = repo.get_commit('da39b1326dbc2edfe518b90672734a08f3c13458').committer_timezone
    assert timezone1 == -7200  # +2 hours
    assert timezone2 == -7200  # +2 hours


@pytest.mark.parametrize('repo', ['test-repos/complex_repo'], indirect=True)
def test_prior_content(repo: Repository):
    modification = repo.get_commit('ffccf1e7497eb8136fd66ed5e42bef29677c4b71').modified_files[0]

    assert modification.content is None
    assert modification.content_before is not None


@pytest.mark.parametrize('repo', ['test-repos/complex_repo'], indirect=True)
def test_previous_source_code(repo: Repository):
    modification = repo.get_commit('ffccf1e7497eb8136fd66ed5e42bef29677c4b71').modified_files[0]

    assert modification.source_code is None
    assert modification.source_code_before is not None


@pytest.mark.parametrize('repo', ['test-repos/source_code_before_commit'], indirect=True)
def test_complete_content_before(repo: Repository):
    modification = repo.get_commit('ca1f75455f064410360bc56218d0418221cf9484').modified_files[0]

    with open('test-repos/source_code_before_commit/sc_A_ca1f75455f064410360bc56218d0418221cf9484.txt', 'rb') as file:
        source_code = file.read()

    assert modification.content == source_code
    assert modification.content_before is None

    previous_source_code = source_code
    with open('test-repos/source_code_before_commit/sc_A_022ebf5fba835c6d95e99eaccc2d85b3db5a2ec0.txt', 'rb') as file:
        source_code = file.read()

    modification = repo.get_commit('022ebf5fba835c6d95e99eaccc2d85b3db5a2ec0').modified_files[0]

    assert modification.content == source_code
    assert modification.content_before == previous_source_code

    previous_source_code = source_code
    modification = repo.get_commit('ecd6780457835a2fc85c532338a29f2c98a6cfeb').modified_files[0]

    assert modification.content is None
    assert modification.content_before == previous_source_code


@pytest.mark.parametrize('repo', ['test-repos/source_code_before_commit'], indirect=True)
def test_complete_source_code_before(repo: Repository):
    modification = repo.get_commit('ca1f75455f064410360bc56218d0418221cf9484').modified_files[0]

    with open('test-repos/source_code_before_commit/sc_A_ca1f75455f064410360bc56218d0418221cf9484.txt') as file:
        source_code = file.read()

    assert modification.source_code == source_code
    assert modification.content is not None
    assert modification.content.decode("utf-8") == source_code
    assert modification.source_code_before is None

    previous_source_code = source_code
    with open('test-repos/source_code_before_commit/sc_A_022ebf5fba835c6d95e99eaccc2d85b3db5a2ec0.txt') as file:
        source_code = file.read()

    modification = repo.get_commit('022ebf5fba835c6d95e99eaccc2d85b3db5a2ec0').modified_files[0]

    assert modification.source_code == source_code
    assert modification.content is not None
    assert modification.content.decode("utf-8") == source_code
    assert modification.source_code_before == previous_source_code
    assert modification.content_before is not None
    assert modification.content_before.decode("utf-8") == previous_source_code

    previous_source_code = source_code
    modification = repo.get_commit('ecd6780457835a2fc85c532338a29f2c98a6cfeb').modified_files[0]

    assert modification.source_code is None
    assert modification.content is None
    assert modification.source_code_before == previous_source_code
    assert modification.content_before is not None
    assert modification.content_before.decode("utf-8") == previous_source_code


@pytest.mark.parametrize('repo', ['test-repos/small_repo'], indirect=True)
def test_stats_all_additions(repo: Repository):
    commit = repo.get_commit('a88c84ddf42066611e76e6cb690144e5357d132c')

    assert commit.insertions == 191
    assert commit.lines == 191
    assert commit.files == 2
    assert commit.deletions == 0


@pytest.mark.parametrize('repo', ['test-repos/small_repo'], indirect=True)
def test_stats_all_deletions(repo: Repository):
    commit = repo.get_commit('6411e3096dd2070438a17b225f44475136e54e3a')

    assert commit.insertions == 0
    assert commit.lines == 4
    assert commit.files == 1
    assert commit.deletions == 4


@pytest.mark.parametrize('repo', ['test-repos/small_repo'], indirect=True)
def test_stats_rename(repo: Repository):
    commit = repo.get_commit('da39b1326dbc2edfe518b90672734a08f3c13458')

    assert commit.insertions == 0
    assert commit.lines == 3
    assert commit.files == 1
    assert commit.deletions == 3


@pytest.mark.parametrize('repo', ['test-repos/complex_repo'], indirect=True)
def test_stats_add_and_delete(repo: Repository):
    commit = repo.get_commit('e7d13b0511f8a176284ce4f92ed8c6e8d09c77f2')

    assert commit.insertions == 1
    assert commit.lines == 2
    assert commit.files == 1
    assert commit.deletions == 1


@pytest.mark.parametrize("repo", ["test-repos/complex_repo"], indirect=True)
def test_commit_dictionary_set(repo: Repository):
    commit1 = repo.get_commit("e7d13b0511f8a176284ce4f92ed8c6e8d09c77f2")
    commit2 = repo.get_commit(commit1.parents[0])
    commit3 = repo.get_commit("a4ece0762e797d2e2dcbd471115108dd6e05ff58")

    commit_dictionary = {commit1: commit1.hash, commit2: commit2.hash, commit3: commit3.hash}

    assert isinstance(commit_dictionary, dict)
    assert commit_dictionary[commit1] == "e7d13b0511f8a176284ce4f92ed8c6e8d09c77f2"
    assert commit_dictionary[commit2] == commit1.parents[0]
    assert commit_dictionary[commit3] == "a4ece0762e797d2e2dcbd471115108dd6e05ff58"
    assert commit_dictionary[commit1] != commit_dictionary[commit2]

    commit_set = {commit1, commit2, commit3}
    assert isinstance(commit_set, set)
    assert commit1 in commit_set
    assert commit_set - {commit1} == {commit2, commit3}


@pytest.mark.parametrize("repo", ["test-repos/complex_repo"], indirect=True)
def test_modification_dictionary_set(repo: Repository):
    commit1 = repo.get_commit("e7d13b0511f8a176284ce4f92ed8c6e8d09c77f2")
    commit2 = repo.get_commit(commit1.parents[0])

    modification1 = commit1.modified_files[0]
    modifications2 = commit2.modified_files

    modification_dictionary = {modification1: commit1, modifications2[0]: commit2, modifications2[1]: commit2}

    assert isinstance(modification_dictionary, dict)
    assert modification_dictionary[modification1].hash == "e7d13b0511f8a176284ce4f92ed8c6e8d09c77f2"
    assert modification_dictionary[modifications2[0]].hash == commit1.parents[0]
    assert modification_dictionary[modifications2[1]].hash == commit1.parents[0]
    assert modification1 != modifications2[0]

    modification_set = {modification1}.union(set(modifications2))
    assert isinstance(modification_set, set)
    assert modification1 in modification_set
    assert modification_set - {modification1} == set(modifications2)


@pytest.mark.parametrize('repo', ['test-repos/multiple_authors'], indirect=True)
def test_multiple_authors(repo: Repository):
    commit = repo.get_commit('a455e6c8ba6960aa8b89bd0fd5f9abefcd10bcd6')

    assert commit.co_authors[0].name == "Somebody"
    assert commit.co_authors[0].email == "some@body.org"