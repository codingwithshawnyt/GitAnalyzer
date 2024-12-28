import pytest

from gitanalyzer import Repository, ChangedFile

@pytest.fixture()
def changed_file(request):
    repo_path, commit_hash = request.param
    repo = Repository(repo_path)
    yield repo.get_commit(commit_hash).changed_files[0]
    repo.cleanup()

@pytest.mark.parametrize('changed_file',
                         [("https://github.com/codingwithshawnyt/GitAnalyzer/diff", "9a985d4a12a3a12f009ef39750fd9b2187b766d1")],
                         indirect=True)
def test_parse_diff_lines(changed_file: ChangedFile):
    assert changed_file.diff_parsed
    additions = changed_file.diff_parsed['added']
    removals = changed_file.diff_parsed['deleted']

    assert (127, '            RevCommit root = rw.parseCommit(headId);') in removals
    assert (128, '            rw.sort(RevSort.REVERSE);') in removals
    assert (129, '            rw.markStart(root);') in removals
    assert (130, '            RevCommit lastCommit = rw.next();') in removals
    assert (131, '            throw new RuntimeException("Changing this line " + path);') in additions

@pytest.mark.parametrize('changed_file',
                         [("https://github.com/codingwithshawnyt/GitAnalyzer/diff", "f45ee2f8976d5f018a1e4ec83eb4556a3df8b0a5")],
                         indirect=True)
def test_check_additions(changed_file: ChangedFile):
    assert changed_file.diff_parsed
    additions = changed_file.diff_parsed['added']
    removals = changed_file.diff_parsed['deleted']

    assert (127, '            RevCommit root = rw.parseCommit(headId);') in additions
    assert (128, '            rw.sort(RevSort.REVERSE);') in additions
    assert (129, '            rw.markStart(root);') in additions
    assert (130, '            RevCommit lastCommit = rw.next();') in additions
    assert (131, '') in additions
    assert len(removals) == 0
    assert len(additions) == 5

@pytest.mark.parametrize('changed_file',
                         [("https://github.com/codingwithshawnyt/GitAnalyzer/diff", "147c7ce9f725a0e259d63f0bf4e6c8ac085ff8c8")],
                         indirect=True)
def test_check_deletions(changed_file: ChangedFile):
    assert changed_file.diff_parsed
    additions = changed_file.diff_parsed['added']
    removals = changed_file.diff_parsed['deleted']

    assert (184, '            List<ChangeSet> allCs = new ArrayList<>();') in removals
    assert (221, '    private GregorianCalendar convertToDate(RevCommit revCommit) {') in removals
    assert (222, '        GregorianCalendar date = new GregorianCalendar();') in removals
    assert (223, '        date.setTimeZone(revCommit.getAuthorIdent().getTimeZone());') in removals
    assert (224, '        date.setTime(revCommit.getAuthorIdent().getWhen());') in removals
    assert (225, '') in removals
    assert (226, '        return date;') in removals
    assert (227, '    }') in removals
    assert (228, '') in removals
    assert (301, '        if(!collectConfig.isCollectingBranches())') in removals
    assert (302, '            return new HashSet<>();') in removals
    assert (303, '') in removals
    assert len(removals) == 12
    assert len(additions) == 0

@pytest.mark.parametrize('changed_file',
                         [("https://github.com/codingwithshawnyt/GitAnalyzer/no_newline", "52a78c1ee5d100528eccba0a3d67371dbd22d898")],
                         indirect=True)
def test_diff_end_without_newline(changed_file: ChangedFile):
    """
    This test verifies that the end-of-file without a newline is correctly interpreted in diffs,
    which git indicates with '\\ No newline at end of file'.
    """
    assert changed_file.diff_parsed
    additions = changed_file.diff_parsed['added']
    removals = changed_file.diff_parsed['deleted']

    assert (1, 'test1') in removals  # considered as removed due to the addition of a newline
    assert (1, 'test1') in additions  # now with an added newline
    assert (2, 'test2') in additions