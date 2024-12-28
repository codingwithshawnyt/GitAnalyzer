from gitanalyzer.repository import Repository
import pytest
from datetime import datetime, timezone, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# Test timestamps setup
TZ_PLUS_1 = timezone(timedelta(hours=1))
TZ_PLUS_2 = timezone(timedelta(hours=2))

TIME_1 = datetime(2018, 3, 22, 10, 41, 30, tzinfo=TZ_PLUS_1)
TIME_2 = datetime(2018, 3, 22, 10, 41, 45, tzinfo=TZ_PLUS_1)
TIME_3 = datetime(2018, 3, 22, 10, 42, 3, tzinfo=TZ_PLUS_1)
TIME_4 = datetime(2018, 3, 27, 17, 20, 3, tzinfo=TZ_PLUS_2)

# Test fixtures
@pytest.fixture
def time_range_repository(request):
    """Fixture for testing time-based repository filtering"""
    start_time, end_time = request.param
    return list(Repository('test-repos/small_repo/', since=start_time, to=end_time).traverse_commits())

@pytest.fixture
def commit_range_repository(request):
    """Fixture for testing commit hash-based repository filtering"""
    start_hash, end_hash = request.param
    return list(Repository('test-repos/small_repo/', 
                         from_commit=start_hash, 
                         to_commit=end_hash).traverse_commits())

@pytest.fixture
def complex_commit_repository(request):
    """Fixture for testing commit ranges in larger repository"""
    start_hash, end_hash = request.param
    return list(Repository('test-repos/refactoring-toy-example/', 
                         from_commit=start_hash, 
                         to_commit=end_hash).traverse_commits())

@pytest.fixture
def tag_range_repository(request):
    """Fixture for testing tag-based repository filtering"""
    start_tag, end_tag = request.param
    return list(Repository('test-repos/small_repo/', 
                         from_tag=start_tag, 
                         to_tag=end_tag).traverse_commits())

@pytest.fixture
def complex_tag_repository(request):
    """Fixture for testing tag ranges in repository with multiple tags"""
    start_tag, end_tag = request.param
    return list(Repository('test-repos/tags',
                         from_tag=start_tag,
                         to_tag=end_tag).traverse_commits())

# Time-based filtering tests
@pytest.mark.parametrize('time_range_repository,expected_count', [
    ((None, None), 5),
    ((None, TIME_1), 1),
    ((None, TIME_2), 1),
    ((None, TIME_3), 3),
    ((None, TIME_4), 4),
], indirect=['time_range_repository'])
def test_end_time_filtering(time_range_repository, expected_count):
    assert len(time_range_repository) == expected_count

@pytest.mark.parametrize('time_range_repository,expected_count', [
    ((None, None), 5),
    ((TIME_1, None), 4),
    ((TIME_2, None), 4),
    ((TIME_3, None), 3),
    ((TIME_4, None), 1),
], indirect=['time_range_repository'])
def test_start_time_filtering(time_range_repository, expected_count):
    assert len(time_range_repository) == expected_count

@pytest.mark.parametrize('time_range_repository,expected_count', [
    ((TIME_2, TIME_4), 3),
    ((TIME_1, TIME_4), 3),
    ((TIME_3, TIME_4), 2),
], indirect=['time_range_repository'])
def test_time_range_filtering(time_range_repository, expected_count):
    assert len(time_range_repository) == expected_count

# Commit hash-based filtering tests
@pytest.mark.parametrize('commit_range_repository,expected_count', [
    ((None, '6411e3096dd2070438a17b225f44475136e54e3a'), 2),
    ((None, '09f6182cef737db02a085e1d018963c7a29bde5a'), 3),
    ((None, '1f99848edadfffa903b8ba1286a935f1b92b2845'), 4),
    ((None, 'HEAD'), 5),
], indirect=['commit_range_repository'])
def test_end_commit_filtering(commit_range_repository, expected_count):
    assert len(commit_range_repository) == expected_count

@pytest.mark.parametrize('complex_commit_repository,expected_count', [
    ((None, '05c1e773878bbacae64112f70964f4f2f7944398'), 9),
    ((None, '76b12f8bd6559f9ab1c830ae2b4be2afad16ec22'), 27),
    ((None, 'ef3422578c0bcaef1561980ef077d06c3f6fc9f9'), 59),
    ((None, '9a5c33b16d07d62651ea80552e8782974c96bb8a'), 64),
    ((None, 'HEAD'), 65),
], indirect=['complex_commit_repository'])
def test_end_commit_filtering_complex(complex_commit_repository, expected_count):
    assert len(complex_commit_repository) == expected_count

@pytest.mark.parametrize('commit_range_repository,expected_count', [
    (('6411e3096dd2070438a17b225f44475136e54e3a', None), 4),
    (('09f6182cef737db02a085e1d018963c7a29bde5a', None), 3),
    (('1f99848edadfffa903b8ba1286a935f1b92b2845', None), 2),
    (('HEAD', None), 1)
], indirect=['commit_range_repository'])
def test_start_commit_filtering(commit_range_repository, expected_count):
    assert len(commit_range_repository) == expected_count

@pytest.mark.parametrize('complex_commit_repository,expected_count', [
    (('0bb0526b70870d57cbac9fcc8c4a7346a4ce5879', None), 4),
    (('1328d7873efe6caaffaf635424e19a4bb5e786a8', None), 8),
    (('5849e143567474f037950f005d994729de0775fc', None), 30),
    (('05c1e773878bbacae64112f70964f4f2f7944398', None), 56),
    (('819b202bfb09d4142dece04d4039f1708735019b', None), 65),
    (('HEAD', None), 1)
], indirect=['complex_commit_repository'])
def test_start_commit_filtering_complex(complex_commit_repository, expected_count):
    assert len(complex_commit_repository) == expected_count

@pytest.mark.parametrize('commit_range_repository,expected_count', [
    (('6411e3096dd2070438a17b225f44475136e54e3a', '09f6182cef737db02a085e1d018963c7a29bde5a'), 2),
    (('09f6182cef737db02a085e1d018963c7a29bde5a', '6411e3096dd2070438a17b225f44475136e54e3a'), 2),
    (('6411e3096dd2070438a17b225f44475136e54e3a', 'HEAD'), 4),
    (('09f6182cef737db02a085e1d018963c7a29bde5a', 'HEAD'), 3),
], indirect=['commit_range_repository'])
def test_commit_range_filtering(commit_range_repository, expected_count):
    assert len(commit_range_repository) == expected_count

@pytest.mark.parametrize('complex_commit_repository,expected_count', [
    (('cd61fd2a70828030ccb3cf46d8719f8b204c52ed', 'e78b02fe027621aec1227cbf5555c75775ba296b'), 6),
    (('40950c317bd52ea5ce4cf0d19707fe426b66649c', '3bfbc107eac92f388de9f8b87682c3a0baf74981'), 10),
    (('e78b02fe027621aec1227cbf5555c75775ba296b', 'e6237f795546c5f14765330ceebe44cd41cdfffe'), 45),
    (('cd61fd2a70828030ccb3cf46d8719f8b204c52ed', '9a5c33b16d07d62651ea80552e8782974c96bb8a'), 63),
], indirect=['complex_commit_repository'])
def test_commit_range_filtering_complex(complex_commit_repository, expected_count):
    assert len(complex_commit_repository) == expected_count

@pytest.mark.parametrize('complex_commit_repository,expected_count', [
    (('c286db365e7374fe4d08f54077abb7fba81dd296', None), 5),
    (('e6237f795546c5f14765330ceebe44cd41cdfffe', None), 10),
    (('b95891f09907aaa0c6dfc6012a7b3add6b33a9b1', None), 21),
    (('e78b02fe027621aec1227cbf5555c75775ba296b', None), 59),
], indirect=['complex_commit_repository'])
def test_merge_commit_start_filtering(complex_commit_repository, expected_count):
    assert len(complex_commit_repository) == expected_count

@pytest.mark.parametrize('complex_commit_repository,expected_count', [
    (('36287f7c3b09eff78395267a3ac0d7da067863fd', 'e78b02fe027621aec1227cbf5555c75775ba296b'), 5),
    (('70b71b7fd3c5973511904c468e464d4910597928', '90c0927162e4cef50fd65da6715932f908264d24'), 9),
    (('70b71b7fd3c5973511904c468e464d4910597928', 'c286db365e7374fe4d08f54077abb7fba81dd296'), 54),
    (('3bfbc107eac92f388de9f8b87682c3a0baf74981', 'c286db365e7374fe4d08f54077abb7fba81dd296'), 24),
], indirect=['complex_commit_repository'])
def test_merge_commit_range_filtering(complex_commit_repository, expected_count):
    assert len(complex_commit_repository) == expected_count

# Tag-based filtering tests
@pytest.mark.parametrize('tag_range_repository,expected_count', [
    ((None, 'v1.4'), 3),
], indirect=['tag_range_repository'])
def test_end_tag_filtering(tag_range_repository, expected_count):
    assert len(tag_range_repository) == expected_count

@pytest.mark.parametrize('tag_range_repository,expected_count', [
    (('v1.4', None), 3),
], indirect=['tag_range_repository'])
def test_start_tag_filtering(tag_range_repository, expected_count):
    assert len(tag_range_repository) == expected_count

@pytest.mark.parametrize('complex_tag_repository,expected_count', [
    (('tag1', 'tag2'), 3),
    (('tag1', 'tag3'), 5),
    (('tag2', 'tag3'), 3),
], indirect=['complex_tag_repository'])
def test_tag_range_filtering(complex_tag_repository, expected_count):
    assert len(complex_tag_repository) == expected_count


# Tests for merge commit handling
@pytest.mark.parametrize('repository_mining_cc_complex,expected_commits', [
    (('c286db365e7374fe4d08f54077abb7fba81dd296', None), 5),
    (('e6237f795546c5f14765330ceebe44cd41cdfffe', None), 10),
    (('b95891f09907aaa0c6dfc6012a7b3add6b33a9b1', None), 21),
    (('e78b02fe027621aec1227cbf5555c75775ba296b', None), 59),
], indirect=['repository_mining_cc_complex'])
def test_merge_commit_start_point(repository_mining_cc_complex, expected_commits):
    """Test repository traversal starting from merge commits"""
    assert len(repository_mining_cc_complex) == expected_commits


@pytest.mark.parametrize('repository_mining_cc_complex,expected_commits', [
    (('36287f7c3b09eff78395267a3ac0d7da067863fd', 'e78b02fe027621aec1227cbf5555c75775ba296b'), 5),
    (('70b71b7fd3c5973511904c468e464d4910597928', '90c0927162e4cef50fd65da6715932f908264d24'), 9),
    (('70b71b7fd3c5973511904c468e464d4910597928', 'c286db365e7374fe4d08f54077abb7fba81dd296'), 54),
    (('3bfbc107eac92f388de9f8b87682c3a0baf74981', 'c286db365e7374fe4d08f54077abb7fba81dd296'), 24),
], indirect=['repository_mining_cc_complex'])
def test_merge_commit_range(repository_mining_cc_complex, expected_commits):
    """Test repository traversal between merge commits"""
    assert len(repository_mining_cc_complex) == expected_commits


# Tag-based filtering tests
@pytest.mark.parametrize('repository_mining_tt,expected_commits', [
    ((None, 'v1.4'), 3),
], indirect=['repository_mining_tt'])
def test_tag_end_filter(repository_mining_tt, expected_commits):
    """Test repository filtering with end tag"""
    assert len(repository_mining_tt) == expected_commits


@pytest.mark.parametrize('repository_mining_tt,expected_commits', [
    (('v1.4', None), 3),
], indirect=['repository_mining_tt'])
def test_tag_start_filter(repository_mining_tt, expected_commits):
    """Test repository filtering with start tag"""
    assert len(repository_mining_tt) == expected_commits


@pytest.mark.parametrize('repository_mining_complex_tags,expected_commits', [
    (('tag1', 'tag2'), 3),
    (('tag1', 'tag3'), 5),
    (('tag2', 'tag3'), 3),
], indirect=['repository_mining_complex_tags'])
def test_tag_range(repository_mining_complex_tags, expected_commits):
    """Test repository filtering with tag range"""
    assert len(repository_mining_complex_tags) == expected_commits


def test_invalid_filter_combinations():
    """Test that invalid combinations of filters raise exceptions"""
    test_commit = '6411e3096dd2070438a17b225f44475136e54e3a'
    test_tag = 'v1.4'
    test_date = datetime(2018, 3, 22, 10, 41, 30, tzinfo=timezone(timedelta(hours=1)))
    repo_path = 'test-repos/small_repo/'

    # Test incompatible datetime and commit combinations
    with pytest.raises(Exception):
        Repository(repo_path, since=test_date, from_commit=test_commit).traverse_commits()

    # Test incompatible datetime and tag combinations
    with pytest.raises(Exception):
        Repository(repo_path, since=test_date, from_tag=test_tag).traverse_commits()

    # Test incompatible commit and tag combinations
    with pytest.raises(Exception):
        Repository(repo_path, from_commit=test_commit, from_tag=test_tag).traverse_commits()

    # Test incompatible end datetime and commit combinations
    with pytest.raises(Exception):
        Repository(repo_path, to=test_date, to_commit=test_commit).traverse_commits()

    # Test incompatible end datetime and tag combinations
    with pytest.raises(Exception):
        Repository(repo_path, to=test_date, to_tag=test_tag).traverse_commits()

    # Test incompatible single commit with other filters
    with pytest.raises(Exception):
        Repository(repo_path, single=test_commit, to=test_date, to_tag=test_tag).traverse_commits()