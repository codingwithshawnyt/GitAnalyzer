"""
Analyzes and computes statistics about files changed in each commit.
"""
from statistics import mean
from typing import Optional, List

from gitanalyzer.metrics.process.process_metric import ProcessMetric


class CommitFileSetAnalyzer(ProcessMetric):
    """
    Analyzes the number of files modified in each commit to calculate:
    
    1. Highest number of files changed in a single commit
    2. Mean number of files changed across all commits
    
    This metric helps understand commit granularity and developer habits.
    """

    def __init__(self, 
                 repository_path: str,
                 start_date=None,
                 end_date=None,
                 start_commit: Optional[str] = None,
                 end_commit: Optional[str] = None):
        
        super().__init__(
            repository_path, 
            since=start_date, 
            to=end_date, 
            from_commit=start_commit, 
            to_commit=end_commit
        )
        self._files_per_commit: List[int] = []
        self._collect_commit_data()

    def _collect_commit_data(self) -> None:
        """
        Analyzes repository history and stores the number of modified files
        for each commit.
        """
        for commit in self.repo_miner.traverse_commits():
            modified_file_count = len(commit.modified_files)
            self._files_per_commit.append(modified_file_count)

    def get_maximum(self) -> int:
        """
        Calculates the highest number of files changed in any single commit.

        Returns:
            int: Maximum number of files changed in a commit, or 0 if no commits exist
        """
        return max(self._files_per_commit, default=0)

    def get_average(self) -> int:
        """
        Calculates the average number of files changed per commit.

        Returns:
            int: Average number of files per commit rounded to nearest integer,
                 or 0 if no commits exist
        """
        if not self._files_per_commit:
            return 0
            
        return round(mean(self._files_per_commit))
