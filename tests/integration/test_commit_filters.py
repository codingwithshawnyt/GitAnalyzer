import logging
from datetime import datetime, timezone, timedelta
from gitanalyzer.repository import Repository
from git import Repo

import pytest

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                   level=logging.INFO)


def test_modifications_by_extension():
    commits = list(Repository('test-repos/different_files',
                            only_modifications_with_file_types=['.java']).traverse_commits())

    assert commits[0].hash == 'a1b6136f978644ff1d89816bc0f2bd86f6d9d7f5'
    assert commits[1].hash == 'b8c2be250786975f1c6f47e96922096f1bb25e39'
    assert len(commits) == 2

    commits = list(Repository('test-repos/different_files1',
                            only_modifications_with_file_types=['.java'])
                  .traverse_commits())

    assert commits[0].hash == '5adbb71167e79ab6b974827e74c9da4d81977655'
    assert commits[1].hash == '0577bec2387ee131e1ccf336adcc172224d3f6f9'
    assert len(commits) == 2


def test_empty_extension_modifications():
    commits = list(Repository('test-repos/different_files',
                            only_modifications_with_file_types=['.py'])
                  .traverse_commits())

    assert len(commits) == 0


def test_extension_and_date_filter():
    timezone_offset = timezone(timedelta(hours=2))
    cutoff_date = datetime(2016, 10, 8, 23, 57, 49, tzinfo=timezone_offset)
    print(cutoff_date)
    
    commits = list(Repository('test-repos/different_files',
                            only_modifications_with_file_types=['.java'],
                            since=cutoff_date)
                  .traverse_commits())

    print(commits)
    assert commits[0].hash == 'b8c2be250786975f1c6f47e96922096f1bb25e39'
    assert len(commits) == 1


def test_main_branch_only():
    commits = list(Repository('test-repos/branches_not_merged').traverse_commits())

    assert commits[0].hash == '04b0af7b53c2a0095e98951571aa41c2e0e0dbec'
    assert commits[1].hash == 'e51421e0beae6a3c20bdcdfc21066e05db675e03'
    assert commits[2].hash == 'b197ef4f0b4bc5b7d55c8949ecb1c861731f0b9d'
    assert len(commits) == 3


def test_exclude_merge_commits():
    commits = list(Repository('test-repos/branches_merged',
                            only_no_merge=True).traverse_commits())

    assert commits[0].hash == '168b3aab057ed61a769acf336a4ef5e64f76c9fd'
    assert commits[1].hash == '8169f76a3d7add54b4fc7bca7160d1f1eede6eda'
    assert commits[2].hash == '8986af2a679759e5a15794f6d56e6d46c3f302f1'
    assert len(commits) == 3


def test_unfiltered_commits():
    commits = list(Repository('test-repos/different_files').traverse_commits())

    assert commits[0].hash == 'a1b6136f978644ff1d89816bc0f2bd86f6d9d7f5'
    assert commits[1].hash == '375de7a8275ecdc0b28dc8de2568f47241f443e9'
    assert commits[2].hash == 'b8c2be250786975f1c6f47e96922096f1bb25e39'
    assert len(commits) == 3


def test_specific_branch():
    commits = list(Repository('test-repos/branches_not_merged',
                            only_in_branch='b1').traverse_commits())
    
    assert commits[0].hash == '04b0af7b53c2a0095e98951571aa41c2e0e0dbec'
    assert commits[1].hash == 'e51421e0beae6a3c20bdcdfc21066e05db675e03'
    assert commits[2].hash == 'b197ef4f0b4bc5b7d55c8949ecb1c861731f0b9d'
    assert commits[3].hash == '87a31153090808f1e6f679a14ea28729a0b74f4d'
    assert commits[4].hash == '702d469710d2087e662c210fd0e4f9418ec813fd'
    assert len(commits) == 5


def test_branch_analysis():
    repo_path = 'test-repos/branches_not_merged'
    
    # Default master branch analysis
    master_commits = len(list(Repository(repo_path).traverse_commits()))
    assert master_commits == 3
    
    # B2 branch analysis
    b2_commits = len(list(Repository(repo_path, only_in_branch='b2')
                         .traverse_commits()))
    assert b2_commits == 4
    
    # B1 branch analysis
    b1_commits = len(list(Repository(repo_path, only_in_branch='b1')
                         .traverse_commits()))
    assert b1_commits == 5


def test_invalid_branch():
    with pytest.raises(Exception):
        list(Repository('test-repos/branches_not_merged', 
                       only_in_branch='branch2').traverse_commits())


def test_author_filter():
    repo_path = 'test-repos/multiple_authors'
    
    mauricio_commits = list(Repository(repo_path,
                                     only_authors=["Maurício Aniche"])
                           .traverse_commits())
    assert len(mauricio_commits) == 4

    ishepard_commits = list(Repository(repo_path,
                                     only_authors=["ishepard"])
                           .traverse_commits())
    assert len(ishepard_commits) == 1


def test_nonexistent_author():
    commits = list(Repository('test-repos/multiple_authors',
                            only_authors=["Uncle Bob"])
                  .traverse_commits())
    assert len(commits) == 0


def test_specific_commit_selection():
    # Test single commit selection
    selected_commits = list(Repository('test-repos/complex_repo',
                         only_commits=["9e71dd5726d775fb4a5f08506a539216e878adbb"]).traverse_commits())
    assert len(selected_commits) == 1
    assert selected_commits[0].hash == "9e71dd5726d775fb4a5f08506a539216e878adbb"

    # Test multiple commit selection (2 commits)
    commit_list = list(Repository('test-repos/complex_repo',
                         only_commits=["953737b199de233896f00b4d87a0bc2794317253", 
                                     "ffccf1e7497eb8136fd66ed5e42bef29677c4b71"]).traverse_commits())
    assert len(commit_list) == 2
    assert commit_list[0].hash == "ffccf1e7497eb8136fd66ed5e42bef29677c4b71"
    assert commit_list[1].hash == "953737b199de233896f00b4d87a0bc2794317253"

    # Test multiple commit selection (3 commits)
    multiple_commits = list(Repository('test-repos/complex_repo',
                         only_commits=["866e997a9e44cb4ddd9e00efe49361420aff2559",
                                     "57dbd017d1a744b949e7ca0b1c1a3b3dd4c1cbc1",
                                     "e7d13b0511f8a176284ce4f92ed8c6e8d09c77f2"]).traverse_commits())
    assert len(multiple_commits) == 3
    assert multiple_commits[0].hash == "866e997a9e44cb4ddd9e00efe49361420aff2559"
    assert multiple_commits[1].hash == "57dbd017d1a744b949e7ca0b1c1a3b3dd4c1cbc1"
    assert multiple_commits[2].hash == "e7d13b0511f8a176284ce4f92ed8c6e8d09c77f2"

    # Test invalid commit hash
    invalid_commit = list(Repository('test-repos/complex_repo',
                         only_commits=["fake hash"]).traverse_commits())
    assert len(invalid_commit) == 0

    # Test total number of commits
    repo_commits = len(list(Repository('test-repos/complex_repo').traverse_commits()))
    assert repo_commits == 13


def test_individual_commit():
    # Test specific commit
    result = list(Repository('test-repos/complex_repo',
                         single="866e997a9e44cb4ddd9e00efe49361420aff2559").traverse_commits())
    assert len(result) == 1
    assert result[0].hash == "866e997a9e44cb4ddd9e00efe49361420aff2559"

    # Test another specific commit
    commit_result = list(Repository('test-repos/complex_repo',
                         single="ffccf1e7497eb8136fd66ed5e42bef29677c4b71").traverse_commits())
    assert len(commit_result) == 1
    assert commit_result[0].hash == "ffccf1e7497eb8136fd66ed5e42bef29677c4b71"


def test_head_commit():
    specific_commit = list(Repository('test-repos/complex_repo',
                         single="e7d13b0511f8a176284ce4f92ed8c6e8d09c77f2").traverse_commits())
    assert len(specific_commit) == 1

    head_commit = list(Repository('test-repos/complex_repo', single="HEAD").traverse_commits())
    assert len(head_commit) == 1
    assert specific_commit[0].hash == head_commit[0].hash


def test_invalid_commit_scenarios():
    # Test invalid single commit
    with pytest.raises(Exception):
        list(Repository('test-repos/complex_repo', single="ASD").traverse_commits())

    # Test invalid from_commit
    with pytest.raises(Exception):
        list(Repository('test-repos/complex_repo', from_commit="ASD").traverse_commits())

    # Test invalid to_commit
    with pytest.raises(Exception):
        list(Repository('test-repos/complex_repo', to_commit="ASD").traverse_commits())

    # Test invalid from and to commits
    with pytest.raises(Exception):
        list(Repository('test-repos/complex_repo',
             from_commit="ASD",
             to_commit="ASD").traverse_commits())


def test_file_history_with_date():
    cutoff_date = datetime(2018, 6, 6)
    file_commits = len(list(Repository(
        path_to_repo='test-repos/szz',
        filepath='myfolder/H.java',
        to=cutoff_date).traverse_commits()))
    assert file_commits == 5


def test_file_history_since_date():
    start_date = datetime(2018, 6, 6)
    commit_count = len(list(Repository(
        path_to_repo='test-repos/szz',
        filepath='myfolder/H.java',
        since=start_date).traverse_commits()))
    assert commit_count == 11


def test_date_filtering():
    filter_date = datetime(2018, 6, 6, tzinfo=timezone.utc)

    regular_filter = len(list(Repository(
        path_to_repo='test-repos/since_as_filter',
        since=filter_date).traverse_commits()))
    assert regular_filter == 3

    special_filter = len(list(Repository(
        path_to_repo='test-repos/since_as_filter',
        since_as_filter=filter_date).traverse_commits()))
    assert special_filter == 16


def test_file_rename_tracking():
    target_date = datetime(2018, 6, 6)
    file_commits = list(Repository(
        path_to_repo='test-repos/small_repo',
        filepath='file4.java',
        to=target_date).traverse_commits())
    assert len(file_commits) == 2

    commit_ids = [commit.hash for commit in file_commits]
    assert 'da39b1326dbc2edfe518b90672734a08f3c13458' in commit_ids
    assert 'a88c84ddf42066611e76e6cb690144e5357d132c' in commit_ids


def test_complex_file_rename_tracking():
    file_history = list(Repository(
        path_to_repo='test-repos/complex_repo',
        filepath='Matricula.javax').traverse_commits())
    assert len(file_history) == 6

    history_hashes = [commit.hash for commit in file_history]
    expected_hashes = [
        'f0dd1308bd904a9b108a6a40865166ee962af3d4',
        '953737b199de233896f00b4d87a0bc2794317253',
        'a3290ac2f555eabca9e31180cf38e91f9e7e2761',
        '71535a31f0b598a5d5fcebda7146ebc01def783a',
        '57dbd017d1a744b949e7ca0b1c1a3b3dd4c1cbc1',
        '866e997a9e44cb4ddd9e00efe49361420aff2559'
    ]
    for hash_value in expected_hashes:
        assert hash_value in history_hashes


def test_release_commits():
    release_commits = list(Repository('test-repos/tags',
                         only_releases=True).traverse_commits())

    assert len(release_commits) == 3
    assert release_commits[0].hash == '6bb9e2c6a8080e6b5b34e6e316c894b2ddbf7fcd'
    assert release_commits[1].hash == '4638730126d40716e230c2040751a13153fb1556'
    assert release_commits[2].hash == '627e1ad917a188a861c9fedf6e5858b79edbe439'


def test_empty_releases():
    no_releases = list(Repository('test-repos/complex_repo', 
                                only_releases=True).traverse_commits())
    assert len(no_releases) == 0


def test_commit_ordering():
    date_ordered = list(Repository('test-repos/order', 
                                 order='date-order').traverse_commits())
    author_ordered = list(Repository('test-repos/order', 
                                   order='author-date-order').traverse_commits())
    
    expected_hashes = [
        '5e3cfa27b3fe6dd4d12fd89664fea9397141b843',
        '19732de9e2b58ba7285f272810a9d8ddf18e7c89',
        '78a94953a3e140f2d0027fb57963345fbf6d59fe',
        '9cc3af5f242a1eba297f270acbdb8b6628556413',
        '6564f9e0bfb38725ebcfb4547e98e7f545c7de12',
        '5c95c1c6ba95a1bdb12772d1a63c7d331e664819',
        'd23d7f6d37fd1163022a5dd46985acd34e6818d7',
        'a45c8649b00d8b48cee04a822bd1d82acd667db2'
    ]
    
    for i, hash_value in enumerate(expected_hashes):
        assert date_ordered[i].hash == hash_value
        assert author_ordered[i].hash == hash_value

def test_topological_ordering():
    commit_sequence = list(Repository('test-repos/order', order='topo-order').traverse_commits())
    
    expected_sequence = [
        '5e3cfa27b3fe6dd4d12fd89664fea9397141b843',
        '19732de9e2b58ba7285f272810a9d8ddf18e7c89',
        '9cc3af5f242a1eba297f270acbdb8b6628556413',
        'd23d7f6d37fd1163022a5dd46985acd34e6818d7',
        '78a94953a3e140f2d0027fb57963345fbf6d59fe',
        '6564f9e0bfb38725ebcfb4547e98e7f545c7de12',
        '5c95c1c6ba95a1bdb12772d1a63c7d331e664819',
        'a45c8649b00d8b48cee04a822bd1d82acd667db2'
    ]
    
    for idx, expected_hash in enumerate(expected_sequence):
        assert commit_sequence[idx].hash == expected_hash


def test_ascending_commit_traversal():
    commit_history = list(Repository('test-repos/small_repo').traverse_commits())
    expected_hashes = [
        'a88c84ddf42066611e76e6cb690144e5357d132c',
        '6411e3096dd2070438a17b225f44475136e54e3a',
        '09f6182cef737db02a085e1d018963c7a29bde5a',
        '1f99848edadfffa903b8ba1286a935f1b92b2845',
        'da39b1326dbc2edfe518b90672734a08f3c13458'
    ]
    
    assert len(commit_history) == len(expected_hashes)
    for idx, expected_hash in enumerate(expected_hashes):
        assert commit_history[idx].hash == expected_hash


def test_descending_commit_traversal():
    commit_history = list(Repository('test-repos/small_repo',
                                   order='reverse').traverse_commits())
    expected_hashes = [
        'da39b1326dbc2edfe518b90672734a08f3c13458',
        '1f99848edadfffa903b8ba1286a935f1b92b2845',
        '09f6182cef737db02a085e1d018963c7a29bde5a',
        '6411e3096dd2070438a17b225f44475136e54e3a',
        'a88c84ddf42066611e76e6cb690144e5357d132c'
    ]
    
    assert len(commit_history) == len(expected_hashes)
    for idx, expected_hash in enumerate(expected_hashes):
        assert commit_history[idx].hash == expected_hash


def test_filtered_descending_traversal():
    commit_history = list(Repository('test-repos/small_repo',
                                   from_commit='1f99848edadfffa903b8ba1286a935f1b92b2845',
                                   to_commit='6411e3096dd2070438a17b225f44475136e54e3a',
                                   order='reverse').traverse_commits())
    
    expected_hashes = [
        '1f99848edadfffa903b8ba1286a935f1b92b2845',
        '09f6182cef737db02a085e1d018963c7a29bde5a',
        '6411e3096dd2070438a17b225f44475136e54e3a'
    ]
    
    assert len(commit_history) == len(expected_hashes)
    for idx, expected_hash in enumerate(expected_hashes):
        assert commit_history[idx].hash == expected_hash


def test_reversed_filtered_descending_traversal():
    commit_history = list(Repository('test-repos/small_repo',
                                   from_commit='6411e3096dd2070438a17b225f44475136e54e3a',
                                   to_commit='1f99848edadfffa903b8ba1286a935f1b92b2845',
                                   order='reverse').traverse_commits())
    
    expected_hashes = [
        '1f99848edadfffa903b8ba1286a935f1b92b2845',
        '09f6182cef737db02a085e1d018963c7a29bde5a',
        '6411e3096dd2070438a17b225f44475136e54e3a'
    ]
    
    assert len(commit_history) == len(expected_hashes)
    for idx, expected_hash in enumerate(expected_hashes):
        assert commit_history[idx].hash == expected_hash


def test_reference_inclusion():
    # Test without references
    base_commits = list(Repository('test-repos/branches_not_merged/',
                                 include_refs=False).traverse_commits())
    base_commit_hashes = [commit.hash for commit in base_commits]
    assert len(base_commits) == 3

    # Test with references
    ref_commits = list(Repository('test-repos/branches_not_merged/',
                                include_refs=True).traverse_commits())
    ref_commit_hashes = [commit.hash for commit in ref_commits]
    assert len(ref_commits) == 6

    # Find additional commits when including refs
    additional_commits = list(set(ref_commit_hashes) - set(base_commit_hashes))
    assert len(additional_commits) == 3

    expected_additional_commits = [
        '87a31153090808f1e6f679a14ea28729a0b74f4d',  # Initial b1 branch commit
        '702d469710d2087e662c210fd0e4f9418ec813fd',  # b1 branch HEAD
        '7203c0b8220dcc7a59614bc7549799cd203ac072'   # b2 branch HEAD
    ]
    
    for commit_hash in expected_additional_commits:
        assert commit_hash in additional_commits


def test_remote_repository_access():
    repo = Repo('test-repos/gitanalyzer/')
    target_commit = '2fa0d8c57829b086c9372722115a89d11c9bdd35'

    # Verify commit absence before fetch
    initial_commits = [commit.hash for commit in 
                      Repository('test-repos/gitanalyzer/').traverse_commits()]
    assert target_commit not in initial_commits

    # Verify commit still absent after fetch
    repo.git.fetch('--all')
    post_fetch_commits = [commit.hash for commit in 
                         Repository('test-repos/gitanalyzer/').traverse_commits()]
    assert target_commit not in post_fetch_commits

    # Verify commit presence with remote inclusion
    remote_commits = [commit.hash for commit in 
                     Repository('test-repos/gitanalyzer/', 
                              include_remotes=True).traverse_commits()]
    assert target_commit in remote_commits