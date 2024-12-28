"""
Analyzes and tracks the total number of commits associated with each file in a repository.
"""

from gitanalyzer import ModificationType
from gitanalyzer.metrics.process.process_metric import ProcessMetric


class FileCommitCounter(ProcessMetric):
    """
    Tracks and calculates the total number of times each file has been modified
    across the repository's history.

    This metric helps understand which files have undergone the most changes,
    potentially indicating areas of high development activity or maintenance.
    """

    def count(self):
        """
        Analyzes the repository history to count commits per file.

        Returns:
            dict: A mapping of file paths to their respective commit counts.
                 Example: {
                     'src/main.py': 5,
                     'docs/README.md': 3
                 }
        """
        commit_counts = {}
        file_path_mapping = {}  # Tracks file renames throughout history

        # Iterate through repository history
        for commit in self.repo_miner.traverse_commits():
            for file_change in commit.modified_files:
                # Get current file path, accounting for possible previous renames
                current_path = file_path_mapping.get(
                    file_change.new_path,
                    file_change.new_path
                )

                # Update rename mapping if file was renamed
                if file_change.change_type == ModificationType.RENAME:
                    file_path_mapping[file_change.old_path] = current_path

                # Increment commit count for the file
                commit_counts[current_path] = commit_counts.get(current_path, 0) + 1

        return commit_counts
