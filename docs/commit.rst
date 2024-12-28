.. _commit_toplevel:

=============
Commit Object
=============

The Commit object encapsulates all Git commit information and additional metadata. It provides the following attributes:

* **hash** *(str)*: unique identifier of the commit
* **msg** *(str)*: message associated with the commit
* **author** *(Contributor)*: individual who authored the changes (name, email)
* **committer** *(Contributor)*: individual who committed the changes (name, email)
* **author_date** *(datetime)*: timestamp when the commit was authored
* **author_timezone** *(int)*: timezone offset of author (in seconds from epoch)
* **committer_date** *(datetime)*: timestamp when the commit was committed
* **committer_timezone** *(int)*: timezone offset of committer (in seconds from epoch)
* **branches** *(List[str])*: all branches containing this commit
* **in_main_branch** *(Bool)*: indicates if commit exists in main branch
* **merge** *(Bool)*: indicates if this is a merge commit
* **modified_files** *(List[ModifiedFile])*: files changed in this commit (see :ref:`modifiedfile_toplevel`)
* **parents** *(List[str])*: parent commit identifiers
* **project_name** *(str)*: name of the repository
* **project_path** *(str)*: path to the repository
* **deletions** *(int)*: count of removed lines (from --shortstat)
* **insertions** *(int)*: count of added lines (from --shortstat)
* **lines** *(int)*: total lines changed (additions + deletions from --shortstat)
* **files** *(int)*: total files modified (from --shortstat)
* **dmm_unit_size** *(float)*: Delta Maintainability Model size metric
* **dmm_unit_complexity** *(float)*: Delta Maintainability Model complexity metric
* **dmm_unit_interfacing** *(float)*: Delta Maintainability Model interfacing metric


Usage Example::

    from gitanalyzer import Repository

    repo = Repository('path/to/repository')
    for commit in repo.traverse_commits():
        print(
            f'Commit {commit.hash} was authored by {commit.author.name}, '
            f'committed by {commit.committer.name} on {commit.committer_date}'
        )

For more examples and detailed usage, visit: https://github.com/codingwithshawnyt/GitAnalyzer
