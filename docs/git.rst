.. _git_toplevel:

=============
Git Interface
=============

The Git interface provides a convenient wrapper around common Git operations and utilities.
You can perform various operations like checking out commits and analyzing repository history.

Basic Repository Operations
-------------------------

Here's how to switch to a specific commit or branch::

    git_repo = Git('test-repos/git-1/')
    git_repo.checkout('a7053a4dcd627f5f4f213dc9aa002eb1caf926f8')

**Important Note:** Exercise caution when using checkout operations! They modify the repository's
state on disk, which could cause conflicts if multiple processes or threads are accessing
the same repository simultaneously.

Repository Information
--------------------

The interface offers several methods to extract repository data::

    git_repo = Git('test-repos/test1')
    git_repo.get_list_commits()                  # retrieve all repository commits
    git_repo.get_commit('cc5b002')               # fetch a specific commit by hash
    git_repo.files()                             # list all files in current commit
    git_repo.total_commits()                     # count total repository commits
    git_repo.get_commit_from_tag('v1.15')        # retrieve commit associated with tag

Line History Analysis
-------------------

One particularly valuable feature for developers and researchers is the ability to trace
the history of specific code lines. When given a commit, the system can identify which
previous commits last modified the changed lines (particularly useful for tracking down
bug origins).

Note: Starting from GitAnalyzer 1.9, this functionality supports "git hyper-blame" 
(For more details, visit `the documentation <https://commondatastorage.googleapis.com/chrome-infra-docs/flat/depot_tools/docs/html/depot_tools_tutorial.html#_setting_up>`_).
Git hyper-blame allows you to exclude specific commits, such as refactoring changes,
from the analysis.

Example usage::

    # Timeline:
    # - commit abc: modified line 1 in file A
    # - commit def: modified line 2 in file A
    # - commit ghi: modified line 3 in file A
    # - commit lmn: removed lines 1 and 2 from file A
    
    git_repo = Git('test-repos/test5')
    
    target_commit = git_repo.get_commit('lmn')
    historical_commits = git_repo.get_commits_last_modified_lines(target_commit)
    print(historical_commits)      # outputs: (abc, def)

In this example, when commit **lmn** removes lines 1 and 2, GitAnalyzer traces back
to find the commits that last modified these lines (commits **abc** and **def**).

For a comprehensive list of available functions, please refer to the :ref:`api_reference_toplevel`.
