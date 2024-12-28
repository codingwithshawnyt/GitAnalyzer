"""
Analyzes the distribution of developers who have modified files within a repository
during a specified time period.

Reference implementation inspired by:
https://github.com/codingwithshawnyt/GitAnalyzer
"""
from typing import Optional, Dict
from gitanalyzer.repository import ModificationType
from gitanalyzer.metrics.process.base_process_metric import BaseProcessMetric


class FileContributorMetrics(BaseProcessMetric):
    """
    Calculates file-level contribution metrics:

    1. Total Contributor Count: Number of unique developers who have modified each file
    2. Small Contributors: Number of developers whose contributions are minimal
       (defined as less than 5% of total changes to the file)
    """

    def __init__(self, repository_path: str,
                 start_date=None,
                 end_date=None,
                 start_commit: Optional[str] = None,
                 end_commit: Optional[str] = None):

        super().__init__(
            repository_path,
            start_date=start_date,
            end_date=end_date,
            start_commit=start_commit,
            end_commit=end_commit
        )
        self._compute_metrics()

    def _compute_metrics(self) -> None:
        """Initialize and compute all contributor metrics."""
        # Track contribution data
        self._file_contributors: Dict[str, Dict[str, int]] = {}
        self._total_contributors: Dict[str, int] = {}
        self._minimal_contributors: Dict[str, int] = {}
        
        # Track file renames
        file_path_mapping = {}

        # Analyze each commit
        for commit in self.repository.get_commits():
            for changed_file in commit.changed_files:
                # Handle file renames and get current path
                current_path = file_path_mapping.get(
                    changed_file.new_path,
                    changed_file.new_path
                )

                # Update rename mapping
                if changed_file.change_type == ModificationType.RENAME:
                    file_path_mapping[changed_file.old_path] = current_path

                # Calculate lines changed
                total_changes = (
                    changed_file.lines_added + 
                    changed_file.lines_removed
                )

                # Update contributor statistics
                if current_path not in self._file_contributors:
                    self._file_contributors[current_path] = {}

                contributor = commit.author.email.strip()
                self._file_contributors[current_path][contributor] = (
                    self._file_contributors[current_path].get(contributor, 0) +
                    total_changes
                )

        # Calculate final metrics
        self._calculate_contributor_counts()

    def _calculate_contributor_counts(self) -> None:
        """Transform raw contribution data into final metrics."""
        for filepath, contributions in list(self._file_contributors.items()):
            total_lines = sum(contributions.values())

            # Skip files with no changes
            if total_lines == 0:
                del self._file_contributors[filepath]
                continue

            # Calculate metrics
            self._total_contributors[filepath] = len(contributions)
            
            # Count contributors with less than 5% contribution
            small_contributors = sum(
                1 for lines in contributions.values()
                if (lines / total_lines) < 0.05
            )
            self._minimal_contributors[filepath] = small_contributors

    def get_total_contributors(self) -> Dict[str, int]:
        """
        Returns the number of unique contributors per file.
        """
        return self._total_contributors

    def get_minimal_contributors(self) -> Dict[str, int]:
        """
        Returns the count of contributors who made minor changes (< 5% of total)
        to each file.
        """
        return self._minimal_contributors
