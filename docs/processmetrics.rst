.. highlight:: python

==================
Process Metrics
==================

Process metrics focus on the development process rather than the code characteristics.
Starting from version 1.11, GitAnalyzer can compute metrics such as ``change_set``, ``code churn``, ``commits count``, ``contributors count``, ``contributors experience``, ``history complexity``, ``hunks count``, ``lines count``, and ``minor contributors`` all in a single command!

These metrics can be calculated between two specific commits (using the parameters ``from_commit`` and ``to_commit``) or between two dates (using the parameters ``since`` and ``to``).

Here's an example of how to use these metrics.


Change Set
==========

This metric evaluates the number of files committed together.

The ``ChangeSet`` class provides two methods:

* ``max()`` to determine the *maximum* number of files committed together;
* ``avg()`` to calculate the *average* number of files committed together, rounded to the nearest whole number.

Example usage::

    from gitanalyzer.metrics.process.change_set import ChangeSet
    metric = ChangeSet(path_to_repo='path/to/the/repo',
                       from_commit='start commit hash',
                       to_commit='end commit hash')
    
    max_files = metric.max()
    avg_files = metric.avg()
    print('Maximum number of files committed together: {}'.format(max_files))
    print('Average number of files committed together: {}'.format(avg_files))

This will output the maximum and average number of files committed together during the specified period ``[from_commit, to_commit]``.

To use date ranges instead::

    from datetime import datetime
    from gitanalyzer.metrics.process.change_set import ChangeSet
    metric = ChangeSet(path_to_repo='path/to/the/repo',
                       since=datetime(2019, 1, 1),
                       to=datetime(2019, 12, 31))
    
    max_files = metric.max()
    avg_files = metric.avg()
    print('Maximum number of files committed together: {}'.format(max_files))
    print('Average number of files committed together: {}'.format(avg_files))

This code will display the maximum and average number of files committed together between ``1st January 2019`` and ``31st December 2019``.


Code Churn
==========

This metric quantifies the code churns of a file.

Code churn can be calculated as either:
    
    (a) (added lines - removed lines) or 
    (b) (added lines + removed lines)
    
over the selected commits.

The ``CodeChurn`` class includes four methods:

* ``count()`` to determine the *total* code churn size of a file;
* ``max()`` to find the *maximum* code churn size of a file;
* ``avg()`` to compute the *average* code churn size of a file, rounded to the nearest whole number;
* ``get_added_and_removed_lines()`` to fetch the *exact* number of lines added and removed per file as a tuple (added_lines, removed_lines).

Example::

    from gitanalyzer.metrics.process.code_churn import CodeChurn
    metric = CodeChurn(path_to_repo='path/to/the/repo',
                       from_commit='start commit hash',
                       to_commit='end commit hash')
    total_churn = metric.count()
    max_churn = metric.max()
    avg_churn = metric.avg()
    added_removed = metric.get_added_and_removed_lines()
    
    print('Total code churn for each file: {}'.format(total_churn))
    print('Maximum code churn for each file: {}'.format(max_churn))
    print('Average code churn for each file: {}'.format(avg_churn))
    print('Lines added and removed for each file: {}'.format(added_removed))

This will output the total, maximum, and average code churns for each modified file, along with the added and removed lines, during the period ``[from_commit, to_commit]``.

You can configure the calculation method (a or b) by setting the ``CodeChurn`` initialization parameter:

* ``add_deleted_lines_to_churn``

To directly retrieve the added and removed lines for each file, use the ``get_added_and_removed_lines()`` method, which returns a dictionary with file paths as keys and a tuple (added_lines, removed_lines) as values.


Commits Count
=============

This metric counts the number of commits made to a file.

The ``CommitCount`` class has one method:

* ``count()`` to determine the number of commits made to a file.

Example::

    from gitanalyzer.metrics.process.commits_count import CommitsCount
    metric = CommitsCount(path_to_repo='path/to/the/repo',
                          from_commit='start commit hash',
                          to_commit='end commit hash')
    commit_numbers = metric.count()
    print('Number of commits per file: {}'.format(commit_numbers))

This will display the number of commits for each modified file during the period ``[from_commit, to_commit]``.


Contributors Count
==================

This metric evaluates the number of developers who have contributed to a file.

The ``ContributorsCount`` class offers two methods:

* ``count()`` to determine the number of contributors who modified a file;
* ``count_minor()`` to identify the number of *minor* contributors who modified a file, defined as those contributing less than 5% to the file.

Example::

    from gitanalyzer.metrics.process.contributors_count import ContributorsCount
    metric = ContributorsCount(path_to_repo='path/to/the/repo',
                               from_commit='start commit hash',
                               to_commit='end commit hash')
    total_contributors = metric.count()
    minor_contributors = metric.count_minor()
    print('Number of contributors per file: {}'.format(total_contributors))
    print('Number of "minor" contributors per file: {}'.format(minor_contributors))

This will output the number of developers that contributed to each modified file during the period ``[from_commit, to_commit]`` and the number of developers that contributed less than 5% to each file.


Contributors Experience
========================

This metric quantifies the percentage of lines authored by the most significant contributor of a file.

The ``ContributorExperience`` class has one method:

* ``count()`` to determine the percentage of lines authored by the top contributor of a file.

Example::

    from gitanalyzer.metrics.process.contributors_experience import ContributorsExperience
    metric = ContributorsExperience(path_to_repo='path/to/the/repo',
                                    from_commit='start commit hash',
                                    to_commit='end commit hash')
    top_contributor_lines = metric.count()
    print('Percentage of lines by the top contributor per file: {}'.format(top_contributor_lines))

This will display the percentage of lines authored by the top contributor for each modified file during the period ``[from_commit, to_commit]``.


Hunks Count
===========

This metric counts the number of hunks in a file.
A hunk represents a continuous block of changes in a ``diff``, and this metric helps assess how fragmented the changes are across the file.

The ``HunksCount`` class has one method:

* ``count()`` to determine the median number of hunks per file.

Example::

    from gitanalyzer.metrics.process.hunks_count import HunksCount
    metric = HunksCount(path_to_repo='path/to/the/repo',
                        from_commit='start commit hash',
                        to_commit='end commit hash')
    hunk_numbers = metric.count()
    print('Median number of hunks per file: {}'.format(hunk_numbers))

This will output the median number of hunks for each modified file during the period ``[from_commit, to_commit]``.


Lines Count
===========

This metric evaluates the number of added and removed lines in a file.
The ``LinesCount`` class provides seven methods:

* ``count()`` to determine the total number of added and removed lines for each modified file;
* ``count_added()``, ``max_added()`` and ``avg_added()`` to calculate the total, maximum, and average number of added lines for each modified file;
* ``count_removed()``, ``max_removed()`` and ``avg_removed()`` to calculate the total, maximum, and average number of removed lines for each modified file.

**Note:** The average values are rounded to the nearest integer.

For added lines::

    from gitanalyzer.metrics.process.lines_count import LinesCount
    metric = LinesCount(path_to_repo='path/to/the/repo',
                        from_commit='start commit hash',
                        to_commit='end commit hash')
    
    added_total = metric.count_added()
    added_maximum = metric.max_added()
    added_average = metric.avg_added()
    print('Total lines added per file: {}'.format(added_total))
    print('Maximum lines added per file: {}'.format(added_maximum))
    print('Average lines added per file: {}'.format(added_average))

This will display the total, maximum, and average number of lines added for each modified file during the period ``[from_commit, to_commit]``.

For removed lines::

    from gitanalyzer.metrics.process.lines_count import LinesCount
    metric = LinesCount(path_to_repo='path/to/the/repo',
                        from_commit='from commit hash',
                        to_commit='to commit hash')
    
    removed_total = metric.count_removed()
    removed_maximum = metric.max_removed()
    removed_average = metric.avg_removed()
    print('Total lines removed per file: {}'.format(removed_total))
    print('Maximum lines removed per file: {}'.format(removed_maximum))
    print('Average lines removed per file: {}'.format(removed_average))

This will display the total, maximum, and average number of lines removed for each modified file during the period ``[from_commit, to_commit]``.
