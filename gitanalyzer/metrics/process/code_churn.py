"""
Calculates and analyzes code churn metrics for repository files.
Code churn represents the magnitude of changes in terms of line modifications.
"""
from statistics import mean
from typing import Dict, Optional, Tuple

from gitanalyzer import ModificationType
from gitanalyzer.metrics.process.base_metric import BaseProcessMetric


class ChangeVolume(BaseProcessMetric):
    """
    Analyzes the volume of changes (code churn) in repository files over time.
    
    Measures file modifications using two possible approaches:
    1. Net change volume: (additions - deletions)
    2. Total change volume: (additions + deletions)
    
    Provides metrics for:
    - Total change volume over time
    - Largest single-commit change
    - Average change volume per commit
    """

    def __init__(self, repository_path: str,
                 start_date=None,
                 end_date=None,
                 start_commit: Optional[str] = None,
                 end_commit: Optional[str] = None,
                 skip_new_files=False,
                 use_total_changes=False):
        """
        Initialize the change volume analyzer.
        
        Args:
            repository_path: Path to git repository
            start_date: Starting date for analysis
            end_date: Ending date for analysis
            start_commit: Starting commit hash
            end_commit: Ending commit hash
            skip_new_files: Exclude newly added files from analysis
            use_total_changes: Use sum instead of difference of changes
        """
        super().__init__(
            repository_path,
            start_date=start_date,
            end_date=end_date,
            start_commit=start_commit,
            end_commit=end_commit
        )
        self.skip_new_files = skip_new_files
        self.use_total_changes = use_total_changes
        self.line_changes: Dict[str, Tuple[int, int]] = {}
        self.file_changes: Dict[str, list] = {}
        self._collect_changes()

    def _collect_changes(self) -> None:
        """
        Analyze repository history and collect change statistics for each file.
        """
        file_renames = {}

        for commit in self.repository.traverse_commits():
            for changed_file in commit.modified_files:
                current_path = file_renames.get(
                    changed_file.new_path,
                    changed_file.new_path
                )

                # Track file renames
                if changed_file.change_type == ModificationType.RENAME:
                    file_renames[changed_file.old_path] = current_path

                # Skip new files if configured
                if self.skip_new_files and changed_file.change_type == ModificationType.ADD:
                    continue

                # Store raw line changes
                additions = changed_file.added_lines
                deletions = changed_file.deleted_lines
                self.line_changes[current_path] = (additions, deletions)

                # Calculate change volume based on configuration
                if self.use_total_changes:
                    change_volume = additions + deletions
                else:
                    change_volume = additions - deletions

                # Store change history
                if current_path not in self.file_changes:
                    self.file_changes[current_path] = []
                self.file_changes[current_path].append(change_volume)

    def get_line_modifications(self) -> Dict[str, Tuple[int, int]]:
        """
        Get the raw line modification counts for each file.

        Returns:
            Dictionary mapping file paths to (additions, deletions) tuples
        """
        return self.line_changes

    def total_changes(self) -> Dict[str, int]:
        """
        Calculate total change volume for each file across all commits.

        Returns:
            Dictionary mapping file paths to total change volumes
        """
        return {
            path: sum(changes)
            for path, changes in self.file_changes.items()
        }

    def peak_change(self) -> Dict[str, int]:
        """
        Find the maximum change volume for each file in any single commit.

        Returns:
            Dictionary mapping file paths to maximum change volumes
        """
        return {
            path: max(changes)
            for path, changes in self.file_changes.items()
        }

    def average_change(self) -> Dict[str, int]:
        """
        Calculate the average change volume per commit for each file.

        Returns:
            Dictionary mapping file paths to rounded average change volumes
        """
        return {
            path: round(mean(changes))
            for path, changes in self.file_changes.items()
        }
