import logging
from gitanalyzer.repository import Repository

# Configure logging with timestamp, level, and message
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_tag_range_navigation():
    """Test commit traversal between two specified tags"""
    start_tag = 'tag1'
    end_tag = 'tag3'
    
    commit_list = list(Repository(
        'test-repos/tags',
        from_tag=start_tag,
        to_tag=end_tag
    ).traverse_commits())
    
    # Verify expected number of commits
    assert 5 == len(commit_list)
    
    # Verify commit hashes in expected order
    expected_hashes = [
        '6bb9e2c6a8080e6b5b34e6e316c894b2ddbf7fcd',
        'f1a90b8d7b151ceefd3e3dfc0dc1d0e12b5f48d0',
        '4638730126d40716e230c2040751a13153fb1556',
        'a26f1438bd85d6b22497c0e5dae003812becd0bc',
        '627e1ad917a188a861c9fedf6e5858b79edbe439'
    ]
    
    for idx, commit in enumerate(commit_list):
        assert expected_hashes[idx] == commit.hash

def test_multi_repository_tag_analysis():
    """Test analyzing multiple identical repositories between tags"""
    start_tag = 'tag2'
    end_tag = 'tag3'
    
    # Create list of identical repository paths
    repository_paths = ['test-repos/tags'] * 3
    
    commit_list = list(Repository(
        path_to_repo=repository_paths,
        from_tag=start_tag,
        to_tag=end_tag
    ).traverse_commits())
    
    # Verify combined commit count (3 repos * 3 commits each)
    assert 9 == len(commit_list)
