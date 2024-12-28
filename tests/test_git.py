from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest
from git import Git as PyGit

from gitanalyzer.domain.commit import ModificationType
from gitanalyzer.git import Git


@pytest.fixture
def repository(request):
    git_repo = Git(request.param)
    yield git_repo
    git_repo.clear()


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/small_repo/'], indirect=True)
def test_repo_name(repository: Git):
    assert repository.project_name == "small_repo"


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/small_repo/'], indirect=True)
def test_retrieve_head(repository: Git):
    assert repository is not None
    current_head = repository.get_head()
    assert current_head is not None

    assert current_head.hash == 'da39b1326dbc2edfe518b90672734a08f3c13458'
    assert current_head.author_date.timestamp() == 1522164679


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/empty_repo/'], indirect=True)
def test_empty_repository(repository: Git):
    commits = list(repository.get_list_commits())
    assert commits == []


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/small_repo/'], indirect=True)
def test_retrieve_commits(repository: Git):
    commits = list(repository.get_list_commits())

    expected_commits = {'a88c84ddf42066611e76e6cb690144e5357d132c',
                        '6411e3096dd2070438a17b225f44475136e54e3a',
                        '09f6182cef737db02a085e1d018963c7a29bde5a',
                        '1f99848edadfffa903b8ba1286a935f1b92b2845',
                        'da39b1326dbc2edfe518b90672734a08f3c13458'}

    for commit in commits:
        assert commit.hash in expected_commits

    assert len(commits) == 5


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/small_repo/'], indirect=True)
def test_fetch_commit(repository: Git):
    commit = repository.get_commit('09f6182cef737db02a085e1d018963c7a29bde5a')
    target_zone = timezone(timedelta(hours=1))

    assert commit.hash == '09f6182cef737db02a085e1d018963c7a29bde5a'
    assert commit.author.name == 'ishepard'
    assert commit.committer.name == 'ishepard'
    assert commit.author_date.timestamp() == datetime(2018, 3, 22, 10, 42, 3,
                                                      tzinfo=target_zone).timestamp()
    assert len(commit.modified_files) == 1
    assert commit.msg == 'Ooops file2'
    assert commit.in_main_branch is True
    assert commit.insertions == 4
    assert commit.deletions == 0
    assert commit.lines == 4
    assert commit.files == 1


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/detached_head/'], indirect=True)
def test_detached_head_state(repository: Git):
    commit = repository.get_commit('56c5ef54d9d16d2b2255412f9479830b5b97cb99')
    assert commit.in_main_branch is False


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/small_repo/'], indirect=True)
def test_initial_commit(repository: Git):
    commit = repository.get_commit('a88c84ddf42066611e76e6cb690144e5357d132c')
    target_zone = timezone(timedelta(hours=1))

    assert commit.hash == 'a88c84ddf42066611e76e6cb690144e5357d132c'
    assert commit.author.name == 'ishepard'
    assert commit.committer.name == 'ishepard'
    assert commit.author_date.timestamp() == datetime(2018, 3, 22, 10, 41, 11,
                                                      tzinfo=target_zone).timestamp()
    assert commit.committer_date.timestamp() == datetime(2018, 3, 22, 10, 41, 11,
                                                         tzinfo=target_zone).timestamp()
    assert len(commit.modified_files) == 2
    assert commit.msg == 'First commit adding 2 files'
    assert commit.in_main_branch is True

    assert commit.modified_files[0].change_type == ModificationType.ADD
    assert commit.modified_files[1].change_type == ModificationType.ADD


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/files/'], indirect=True)
def test_list_files(repository: Git):
    files = repository.files()
    assert len(files) == 8

    expected_files = (str(Path('https://github.com/codingwithshawnyt/GitAnalyzer/files/tmp1.py')),
                      str(Path('https://github.com/codingwithshawnyt/GitAnalyzer/files/tmp2.py')),
                      str(Path('https://github.com/codingwithshawnyt/GitAnalyzer/files/fold1/tmp3.py')),
                      str(Path('https://github.com/codingwithshawnyt/GitAnalyzer/files/fold1/tmp4.py')),
                      str(Path('https://github.com/codingwithshawnyt/GitAnalyzer/files/fold2/tmp5.py')),
                      str(Path('https://github.com/codingwithshawnyt/GitAnalyzer/files/fold2/tmp6.py')),
                      str(Path('https://github.com/codingwithshawnyt/GitAnalyzer/files/fold2/fold3/tmp7.py')),
                      str(Path('https://github.com/codingwithshawnyt/GitAnalyzer/files/fold2/fold3/tmp8.py')),
                      )
    for file in files:
        assert file.endswith(expected_files)


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/small_repo/'], indirect=True)
def test_commit_count(repository: Git):
    assert repository.total_commits() == 5


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/small_repo/'], indirect=True)
def test_commit_by_tag(repository: Git):
    commit = repository.get_commit_from_tag('v1.4')

    assert commit.hash == '09f6182cef737db02a085e1d018963c7a29bde5a'
    with pytest.raises(IndexError):
        repository.get_commit_from_tag('v1.5')


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/complex_repo'], indirect=True)
def test_files_in_commit(repository: Git):
    repository.checkout('a7053a4dcd627f5f4f213dc9aa002eb1caf926f8')
    files1 = repository.files()
    assert len(files1) == 3
    repository.reset()

    repository.checkout('f0dd1308bd904a9b108a6a40865166ee962af3d4')
    files2 = repository.files()
    assert len(files2) == 2
    repository.reset()

    repository.checkout('9e71dd5726d775fb4a5f08506a539216e878adbb')
    files3 = repository.files()
    assert len(files3) == 3
    repository.reset()


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/complex_repo'], indirect=True)
def test_sequential_commit_checkout(repository: Git):
    repository.checkout('a7053a4dcd627f5f4f213dc9aa002eb1caf926f8')
    repository.checkout('f0dd1308bd904a9b108a6a40865166ee962af3d4')
    repository.checkout('9e71dd5726d775fb4a5f08506a539216e878adbb')
    files3 = repository.files()
    assert len(files3) == 3
    repository.reset()


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/branches_without_files'], indirect=True)
def test_checkout_unmerged_commit(repository: Git):
    repository.checkout('developing')
    files1 = repository.files()
    assert len(files1) == 2

    repository.reset()
    files2 = repository.files()
    assert len(files2) == 1

    repository.checkout('developing')
    files1 = repository.files()
    assert len(files1) == 2
    repository.reset()


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/complex_repo'], indirect=True)
def test_all_commits(repository: Git):
    commits = list(repository.get_list_commits())

    assert len(commits) == 13
    assert commits[0].hash == '866e997a9e44cb4ddd9e00efe49361420aff2559'
    assert commits[12].hash == 'e7d13b0511f8a176284ce4f92ed8c6e8d09c77f2'


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/complex_repo'], indirect=True)
def test_commit_branches(repository: Git):
    commit = repository.get_commit('a997e9d400f742003dea601bb05a9315d14d1124')

    assert len(commit.branches) == 1
    assert 'b2' in commit.branches

    commit = repository.get_commit('866e997a9e44cb4ddd9e00efe49361420aff2559')
    assert len(commit.branches) == 2
    assert 'master' in commit.branches
    assert 'b2' in commit.branches


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/branches_not_merged'], indirect=True)
def test_branches_with_no_merge(repository: Git):
    commit = repository.get_commit('7203c0b8220dcc7a59614bc7549799cd203ac072')
    assert commit.in_main_branch is False

    commit = repository.get_commit('87a31153090808f1e6f679a14ea28729a0b74f4d')
    assert commit.in_main_branch is False

    commit = repository.get_commit('b197ef4f0b4bc5b7d55c8949ecb1c861731f0b9d')
    assert commit.in_main_branch is True

    commit = repository.get_commit('e51421e0beae6a3c20bdcdfc21066e05db675e03')
    assert commit.in_main_branch is True


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/branches_merged'], indirect=True)
def test_master_branch_commit(repository: Git):
    assert repository.get_head().hash == '29e929fbc5dc6a2e9c620069b24e2a143af4285f'

    repository.checkout('8986af2a679759e5a15794f6d56e6d46c3f302f1')

    git_to_change_head = Git('https://github.com/codingwithshawnyt/GitAnalyzer/branches_merged')
    commit = git_to_change_head.get_commit('8169f76a3d7add54b4fc7bca7160d1f1eede6eda')
    assert commit.in_main_branch is False

    repository.reset()
    assert repository.get_head().hash == '29e929fbc5dc6a2e9c620069b24e2a143af4285f'


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/complex_repo'], indirect=True)
def test_commit_details(repository: Git):
    commit = repository.get_commit('866e997a9e44cb4ddd9e00efe49361420aff2559')

    assert commit.author.name == "Maurício Aniche"
    assert commit.author.email == "mauricioaniche@gmail.com"

    assert commit.msg == "Matricula adicionada"
    assert len(commit.modified_files) == 1

    assert commit.modified_files[0].new_path == "Matricula.java"
    assert commit.modified_files[0].diff
    assert commit.modified_files[0].diff.startswith("@@ -0,0 +1,62 @@\n+package model;") is True
    assert commit.modified_files[0].content is not None
    assert commit.modified_files[0].content.decode().startswith("package model;") is True

    assert commit.modified_files[0].source_code is not None
    assert commit.modified_files[0].source_code.startswith("package model;") is True


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/branches_merged'], indirect=True)
def test_merge_state_of_commits(repository: Git):
    commit = repository.get_commit("168b3aab057ed61a769acf336a4ef5e64f76c9fd")
    assert commit.merge is False

    commit = repository.get_commit("8169f76a3d7add54b4fc7bca7160d1f1eede6eda")
    assert commit.merge is False

    commit = repository.get_commit("29e929fbc5dc6a2e9c620069b24e2a143af4285f")
    assert commit.merge is True


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/complex_repo'], indirect=True)
def test_modified_files_count(repository: Git):
    commit = repository.get_commit('866e997a9e44cb4ddd9e00efe49361420aff2559')
    assert commit.modified_files[0].added_lines == 62
    assert commit.modified_files[0].deleted_lines == 0

    commit = repository.get_commit('d11dd6734ff4e60cac3a7b58d9267f138c9e05c7')
    assert commit.modified_files[0].added_lines == 1
    assert commit.modified_files[0].deleted_lines == 1

@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/complex_repo'], indirect=True)
def test_change_types(repository: Git):
    commit = repository.get_commit('866e997a9e44cb4ddd9e00efe49361420aff2559')
    assert commit.modified_files[0].change_type == ModificationType.ADD
    assert commit.modified_files[0].old_path is None

    commit = repository.get_commit('57dbd017d1a744b949e7ca0b1c1a3b3dd4c1cbc1')
    assert commit.modified_files[0].change_type == ModificationType.MODIFY
    assert commit.modified_files[0].new_path == commit.modified_files[0].old_path

    commit = repository.get_commit('ffccf1e7497eb8136fd66ed5e42bef29677c4b71')
    assert commit.modified_files[0].change_type == ModificationType.DELETE
    assert commit.modified_files[0].new_path is None


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/two_modifications/'], indirect=True)
def test_file_differences(repository: Git):
    commit = repository.get_commit('93b4b18673ca6fb5d563bbf930c45cd1198e979b')

    assert len(commit.modified_files) == 2

    for modification in commit.modified_files:
        if modification.filename == 'file4.java':
            assert modification.deleted_lines == 8
            assert modification.added_lines == 0

        if modification.filename == 'file2.java':
            assert modification.deleted_lines == 12
            assert modification.added_lines == 0


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/complex_repo'], indirect=True)
def test_rename_details(repository: Git):
    commit = repository.get_commit('f0dd1308bd904a9b108a6a40865166ee962af3d4')

    assert commit.author.name == "Maurício Aniche"
    assert commit.author.email == "mauricioaniche@gmail.com"

    assert commit.modified_files[0].new_path == "Matricula.javax"
    assert commit.modified_files[0].old_path == "Matricula.java"


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/branches_merged'], indirect=True)
def test_commit_parents(repository: Git):
    merge_commit = repository.get_commit('29e929fbc5dc6a2e9c620069b24e2a143af4285f')
    assert len(merge_commit.parents) == 2
    assert '8986af2a679759e5a15794f6d56e6d46c3f302f1' in merge_commit.parents
    assert '8169f76a3d7add54b4fc7bca7160d1f1eede6eda' in merge_commit.parents

    normal_commit = repository.get_commit('8169f76a3d7add54b4fc7bca7160d1f1eede6eda')
    assert len(normal_commit.parents) == 1
    assert '168b3aab057ed61a769acf336a4ef5e64f76c9fd' in normal_commit.parents


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/tags'], indirect=True)
def test_commit_tags(repository: Git):
    commit = repository.get_commit_from_tag('tag1')
    assert commit.hash == '6bb9e2c6a8080e6b5b34e6e316c894b2ddbf7fcd'

    commit = repository.get_commit_from_tag('tag2')
    assert commit.hash == '4638730126d40716e230c2040751a13153fb1556'

    with pytest.raises(IndexError):
        repository.get_commit_from_tag('tag4')


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/szz/'], indirect=True)
def test_simple_last_modified(repository: Git):
    buggy_commits = repository.get_commits_last_modified_lines(repository.get_commit('e6d3b38a9ef683e8184eac10a0471075c2808bbd'))

    assert len(buggy_commits) == 1
    assert '540c7f31c18664a38190fafb6721b5174ff4a166' in buggy_commits['B.java']


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/szz/'], indirect=True)
def test_multiple_last_modified(repository: Git):
    buggy_commits = repository.get_commits_last_modified_lines(repository.get_commit('9942ee9dcdd1103e5808d544a84e6bc8cade0e54'))

    assert len(buggy_commits) == 1
    assert '2eb905e5e7be414fd184d6b4f1571b142621f4de' in buggy_commits['A.java']
    assert '20a40688521c1802569e60f9d55342c3bfdd772c' in buggy_commits['A.java']
    assert '22505e97dca6f843549b3a484b3609be4e3acf17' in buggy_commits['A.java']


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/szz/'], indirect=True)
def test_rename_and_fix_last_modified(repository: Git):
    buggy_commits = repository.get_commits_last_modified_lines(repository.get_commit('4e287ab8e6dba110219404fb8a43993f3dda674c'))

    assert len(buggy_commits) == 1
    assert '06b9ff31cd3475d9fd9ef668cc0844ab169da726' in buggy_commits['H.java']


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/szz/'], indirect=True)
def test_rename_last_modified(repository: Git):
    buggy_commits = repository.get_commits_last_modified_lines(repository.get_commit('2f2d0dec7cd06de4c2ed11ed010727a54af8ebf8'))

    assert len(buggy_commits) == 1
    assert '00e61714fd76ff110d8da953aa1179809591f5aa' in buggy_commits[str(Path('myfolder/Z.java'))]


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/szz/'], indirect=True)
def test_useless_lines_last_modified(repository: Git):
    buggy_commits = repository.get_commits_last_modified_lines(repository.get_commit('3bc7295c16b7dfc15d5f82eb6962a2774e1b8420'))
    assert len(buggy_commits) == 1
    assert 'c7fc2e870ce03b0b8dc29ed0eeb26d14e235ea3b' in buggy_commits['H.java']


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/szz/'], indirect=True)
def test_useless_lines2_last_modified(repository: Git):
    buggy_commits = repository.get_commits_last_modified_lines(repository.get_commit('4155c421ee5cbb3c34feee7b68aa78a2ee1bbeae'))
    assert len(buggy_commits) == 0


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/szz/'], indirect=True)
def test_single_file_last_modified(repository: Git):
    commit = repository.get_commit('0f726924f96621e4965039123098ba83e39ffba6')
    buggy_commits = None
    for modification in commit.modified_files:
        if modification.filename == 'A.java':
            buggy_commits = repository.get_commits_last_modified_lines(commit, modification)

    assert buggy_commits
    assert len(buggy_commits) == 1
    assert 'e2ed043eb96c05ebde653a44ae733ded9ef90750' in buggy_commits['A.java']
    assert 1 == len(buggy_commits['A.java'])


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/szz/'], indirect=True)
def test_more_modifications_last_modified(repository: Git):
    buggy_commits = repository.get_commits_last_modified_lines(repository.get_commit('c7002fb321a8ba32a28fac200538f7c2ba76f175'))
    assert len(buggy_commits) == 1
    assert '5cb9e9ae44a0949ec91d06a955975289be766f34' in buggy_commits['A.java']


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/small_repo/'], indirect=True)
def test_modified_file_commits(repository: Git):
    commits = repository.get_commits_modified_file('file2.java')

    assert len(commits) == 3
    assert '09f6182cef737db02a085e1d018963c7a29bde5a' in commits
    assert '6411e3096dd2070438a17b225f44475136e54e3a' in commits
    assert 'a88c84ddf42066611e76e6cb690144e5357d132c' in commits


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/small_repo/'], indirect=True)
def test_missing_file_commits(repository: Git):
    commits = repository.get_commits_modified_file('non-existing-file.java')

    assert len(commits) == 0


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/tags'], indirect=True)
def test_tagged_commits(repository: Git):
    tagged_commits = repository.get_tagged_commits()

    assert len(tagged_commits) == 3
    assert '6bb9e2c6a8080e6b5b34e6e316c894b2ddbf7fcd' == tagged_commits[0]
    assert '4638730126d40716e230c2040751a13153fb1556' == tagged_commits[1]
    assert '627e1ad917a188a861c9fedf6e5858b79edbe439' == tagged_commits[2]


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/different_files'], indirect=True)
def test_tagged_commits_without_tags(repository: Git):
    tagged_commits = repository.get_tagged_commits()

    assert len(tagged_commits) == 0


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/szz/'], indirect=True)
def test_hyper_blame_last_modified(repository: Git):
    buggy_commits = repository.get_commits_last_modified_lines(repository.get_commit(
        'e6d3b38a9ef683e8184eac10a0471075c2808bbd'))

    assert len(buggy_commits) == 1
    assert '540c7f31c18664a38190fafb6721b5174ff4a166' in buggy_commits['B.java']


@pytest.mark.skipif(PyGit().version_info < (2, 23),
                    reason="requires git 2.23 or higher")
@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/szz/'], indirect=True)
def test_unblamable_hyper_blame(tmp_path, repository: Git):
    p = tmp_path / "ignore.txt"
    p.write_text("540c7f31c18664a38190fafb6721b5174ff4a166")

    buggy_commits = repository.get_commits_last_modified_lines(repository.get_commit(
        'e6d3b38a9ef683e8184eac10a0471075c2808bbd'),
        hashes_to_ignore_path=str(p))

    assert len(buggy_commits) == 0


@pytest.mark.skipif(PyGit().version_info < (2, 23),
                    reason="requires git 2.23 or higher")
@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/szz/'], indirect=True)
def test_ignore_hash_hyper_blame(tmp_path, repository: Git):
    p = tmp_path / "ignore.txt"
    p.write_text("5cb9e9ae44a0949ec91d06a955975289be766f34")

    buggy_commits = repository.get_commits_last_modified_lines(repository.get_commit(
        'c7002fb321a8ba32a28fac200538f7c2ba76f175'),
        hashes_to_ignore_path=str(p))

    assert len(buggy_commits) == 1
    assert 'c41d270f8abc203c895309235adbd5f3f81d4a45' in buggy_commits['A.java']


@pytest.mark.parametrize('repository', ['https://github.com/codingwithshawnyt/GitAnalyzer/szz/'], indirect=True)
def test_hyper_blame_with_renaming(repository: Git):
    buggy_commits = repository.get_commits_last_modified_lines(repository.get_commit(
        'be0772cbaa2eba32bf97aae885199d1a357ddc93'))

    assert len(buggy_commits) == 2
    assert '9568d20856728304ab0b4d2d02fb9e81d0e5156d' in buggy_commits['A.java']
    assert '9568d20856728304ab0b4d2d02fb9e81d0e5156d' in buggy_commits['H.java']


@pytest.mark.parametrize('repository', ["https://github.com/codingwithshawnyt/GitAnalyzer/diff"], indirect=True)
def test_diff_functionality(repository: Git):
    from_commit_id = "9e9473d5ca310b7663e9df93c402302b6b7f24aa"
    to_commit_id = "b267a14e0503fdac36d280422f16360d1f661f12"
    modified_files = repository.diff(from_commit_id, to_commit_id)

    diff = modified_files[0].diff

    assert len(modified_files) == 1
    assert "@@ -107,7 +107,7 @@ public class GitRepository implements SCM {" in diff
    assert "     }" in diff
    assert "     public static SCMRepository completelyNewName(String path) {" in diff
    assert "-        return allProjectsIn(path, false);" in diff
    assert "+        return new GitRepository(path).info();" in diff
    assert "     }" in diff
    assert "     public static SCMRepository singleProject(String path, boolean singleParentOnly) {" in diff