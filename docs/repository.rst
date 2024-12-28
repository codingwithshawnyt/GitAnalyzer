.. _gitanalyzer_main:

============
GitAnalyzer
============
The `GitAnalyzer` class serves as the core component of the library, designed to extract and process git repository commits. 
One of the key strengths of GitAnalyzer is its extensive configurability, allowing users to fine-tune their repository analysis. Let's explore the various configuration options available.

Getting Started
===============
Here's a basic example to begin with::

    for commit in GitAnalyzer("/path/to/your/repo").get_commits():
        print(commit.hash)

The `get_commits()` method returns an iterator of the specified commits. Without any parameters, it will process *all commits* in the repository.
Let's explore how to customize the `GitAnalyzer` to meet your specific needs.

Repository Selection
===================
The `GitAnalyzer` class requires a **repository_path** parameter, which can be either a single repository or multiple repositories. This parameter accepts both `str` and `List[str]` types.

The library supports both local and remote repositories. When providing a URL, GitAnalyzer automatically handles the cloning process by creating a temporary directory, cloning the repository, performing the analysis, and cleaning up afterward.

Here are some valid initialization examples::

    # Single local repository
    path = "local/repo/path/"
    
    # Multiple local repositories
    path = ["repo1/path/", "repo2/path/"]
    
    # Mixed local and remote repositories
    path = ["local/repo/", "https://github.com/codingwithshawnyt/GitAnalyzer.git", "another/local/repo"]
    
    # Single remote repository
    path = "https://github.com/codingwithshawnyt/GitAnalyzer.git"

To identify which project is being analyzed, you can access the **project_name** property of the `Commit` object.

Commit Range Configuration
=========================

While GitAnalyzer processes all commits by default, you can narrow down the analysis using various filters:

* **commit_hash** *(str)*: Analyze a specific commit by its hash

*START POINT*:

* **start_date** *(datetime)*: Begin analysis from this date
* **start_commit** *(str)*: Start from this commit hash
* **start_tag** *(str)*: Begin from this tag

*END POINT*:

* **end_date** *(datetime)*: Stop analysis at this date
* **end_commit** *(str)*: Stop at this commit hash
* **end_tag** *(str)*: Stop at this tag

*TRAVERSAL ORDER*:

* **traversal_order** *(str)*: Choose between 'date-order', 'author-date-order', 'topo-order', or 'reverse'. **NOTE**: Default ordering is oldest to newest. Use "traversal_order='reverse'" for newest to oldest.

.. _ordering_info: https://git-scm.com/docs/git-rev-list#_commit_ordering

Usage examples::

    # Analyze specific commit
    GitAnalyzer('repo/path', commit_hash='6411e3096dd2070438a17b225f44475136e54e3a').get_commits()

    # Since specific date
    GitAnalyzer('repo/path', start_date=datetime(2016, 10, 8, 17, 0, 0)).get_commits()

    # Date range analysis
    start = datetime(2016, 10, 8, 17, 0, 0)
    end = datetime(2016, 10, 8, 17, 59, 0)
    GitAnalyzer('repo/path', start_date=start, end_date=end).get_commits()

    # Between tags
    GitAnalyzer('repo/path', start_tag='v1.0', end_tag='v2.0').get_commits()

    # Until specific date
    end_date = datetime(2016, 10, 8, 17, 0, 0, tzinfo=timezone)
    GitAnalyzer('repo/path', end_date=end_date).get_commits()

    # !!!!! INVALID !!!!! MULTIPLE START POINTS NOT ALLOWED
    GitAnalyzer('repo/path', start_tag='v1.0', start_commit='abc123').get_commits()

**IMPORTANT**: You cannot combine multiple filters of the same category (e.g., multiple start points) or use the commit_hash filter with other filters!

Commit Filtering
===============

GitAnalyzer provides several filtering options:

* **branch** *(str)*: Analyze commits from a specific branch only
* **exclude_merges** *(bool)*: Skip merge commits
* **authors** *(List[str])*: Filter by commit authors (matches username, not email)
* **commit_list** *(List[str])*: Analyze only specified commit hashes
* **tagged_only** *(bool)*: Include only tagged commits
* **file_path** *(str)*: Filter commits that modified a specific file
* **file_types** *(List[str])*: Filter commits that modified specific file types

Examples::

    # Branch-specific analysis
    GitAnalyzer('repo/path', branch='main').get_commits()

    # Non-merge commits in specific branch
    GitAnalyzer('repo/path', branch='main', exclude_merges=True).get_commits()

    # Author-specific commits
    GitAnalyzer('repo/path', authors=['username']).get_commits()

    # Specific commit set
    GitAnalyzer('repo/path', commit_list=['hash1', 'hash2', 'hash3']).get_commits()

    # File-specific changes
    GitAnalyzer('repo/path', file_path='src/main.cpp').get_commits()

    # File type filtering
    GitAnalyzer('repo/path', file_types=['.cpp']).get_commits()

Advanced Configuration
=====================

Additional configuration options include:

* **include_references** *(bool)*: Include refs and HEAD in analysis (adds :code:`--all`)
* **include_remote_refs** *(bool)*: Include remote references (adds :code:`--remotes`)
* **clone_directory** *(str)*: Specify directory for cloning remote repositories
* **parallel_jobs** *(int)*: Number of parallel processing threads (default: 1, note: commit order not guaranteed if > 1)
* **use_histogram** *(bool)*: Enable histogram diff algorithm
* **ignore_whitespace** *(bool)*: Ignore whitespace changes in diff

.. _diff_algorithms:

Diff Algorithm Options
=====================

Git provides four diff algorithms:

* Myers (default)
* Minimal (Myers enhancement)
* Patience (context-aware)
* Histogram (enhanced patience)

`Detailed algorithm comparison`_

.. _Detailed algorithm comparison: https://git-scm.com/docs/git-diff#Documentation/git-diff.txt---diff-algorithmpatienceminimalhistogrammyers

Research by `Nugroho, et al (2019)`_ shows that different algorithms produce varying results. Their analysis indicates that the Histogram algorithm provides more accurate change detection compared to Myers, particularly in identifying specific code modifications.

.. _Nugroho, et al (2019): https://doi.org/10.1007/s10664-019-09772-z
