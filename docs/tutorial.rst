.. _tutorial_toplevel:

.. highlight:: python

==================
Quick Start Guide
==================

GitAnalyzer is designed to be straightforward and user-friendly. The main component is the `Repository` class, which accepts a repository path and generates an iterator for commit analysis. Here's a basic example::

    for commit in Repository('path/to/your/repository').traverse_commits():
        print('Commit ID: {}, Developer: {}'.format(commit.hash, commit.author.name))

This code snippet will display the developer information for each commit in the repository.

The `Repository` class offers various configuration options to specify which projects, commits, and time periods to analyze. For detailed configuration options, please refer to :ref:`repository_toplevel`.

GitAnalyzer supports analyzing multiple repositories in sequence, including both local and remote sources. When working with remote repositories, GitAnalyzer creates a temporary local clone and removes it after analysis. Here's an example::

    repository_list = [
        "local/repo1",
        "local/repo2",
        "https://github.com/codingwithshawnyt/GitAnalyzer.git",
        "local/repo3",
        "https://github.com/apache/hadoop.git"
    ]
    
    for commit in Repository(path_to_repo=repository_list).traverse_commits():
        print("Repository: {}, Commit ID: {}, Time: {}".format(
               commit.project_path, commit.hash, commit.author_date))


Here's another example that shows how to track file modifications in each commit::

    for commit in Repository('path/to/your/repository').traverse_commits():
        for modified_file in commit.modified_files:
            print('Developer {} changed {} in commit {}'.format(
                commit.author.name, modified_file.filename, commit.hash))

Simple as that!

Under the hood, GitAnalyzer interfaces with the Git repository to extract relevant information and provides a generator for commit iteration.

Additionally, GitAnalyzer can compute structural metrics for modified files in each commit. These calculations are powered by `Lizard <https://github.com/terryyin/lizard>`_, a versatile tool that analyzes source code across various programming languages at both class and method levels::

    for commit in Repository('path/to/your/repository').traverse_commits():
        for modified_file in commit.modified_files:
            print('File: {} | Complexity Score: {} | Method Count: {}'.format(
                  modified_file.filename, 
                  modified_file.complexity, 
                  len(modified_file.methods)))
