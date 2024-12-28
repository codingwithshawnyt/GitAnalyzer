"""
Analyzes and computes statistics related to line changes (additions/deletions)
in a git repository's history.
"""
from statistics import mean
from typing import Optional, Dict, List
from gitanalyzer import ChangeType
from gitanalyzer.metrics.process.base_metric import BaseProcessMetric


class FileLineMetrics(BaseProcessMetric):
    """
    Tracks and analyzes line changes across a repository's history.
    
    Provides the following metrics:
    1. Total line changes (additions + deletions)
    2. Line additions:
        - Total count
        - Maximum per commit
        - Average per commit
    3. Line deletions:
        - Total count
        - Maximum per commit
        - Average per commit
    """

    def __init__(self, 
                 repo_path: str,
                 start_date=None,
                 end_date=None,
                 start_commit: Optional[str] = None,
                 end_commit: Optional[str] = None):
        
        super().__init__(
            repo_path, 
            start_date=start_date, 
            end_date=end_date, 
            start_commit=start_commit, 
            end_commit=end_commit
        )
        self._line_stats = self._collect_line_statistics()

    def _collect_line_statistics(self) -> tuple[Dict[str, List[int]], Dict[str, List[int]]]:
        """
        Analyzes repository history to collect line change statistics.
        """
        additions: Dict[str, List[int]] = {}
        deletions: Dict[str, List[int]] = {}
        file_path_mapping = {}

        for commit in self.repository.get_commits():
            for changed_file in commit.changed_files:
                current_path = file_path_mapping.get(
                    changed_file.new_path,
                    changed_file.new_path
                )

                # Track file renames
                if changed_file.change_type == ChangeType.RENAMED:
                    file_path_mapping[changed_file.old_path] = current_path

                # Update line statistics
                if current_path not in additions:
                    additions[current_path] = []
                if current_path not in deletions:
                    deletions[current_path] = []

                additions[current_path].append(changed_file.lines_added)
                deletions[current_path].append(changed_file.lines_removed)

        return additions, deletions

    def get_total_changes(self) -> Dict[str, int]:
        """
        Calculates total line changes (additions + deletions) per file.
        """
        results = {}
        additions, deletions = self._line_stats

        for path in set(additions.keys()) | set(deletions.keys()):
            total = sum(additions.get(path, [0])) + sum(deletions.get(path, [0]))
            results[path] = total

        return results

    def get_total_additions(self) -> Dict[str, int]:
        """
        Calculates total lines added per file.
        """
        return {
            path: sum(changes)
            for path, changes in self._line_stats[0].items()
        }

    def get_max_additions(self) -> Dict[str, int]:
        """
        Finds maximum lines added in a single commit per file.
        """
        return {
            path: max(changes)
            for path, changes in self._line_stats[0].items()
        }

    def get_average_additions(self) -> Dict[str, int]:
        """
        Calculates average lines added per commit per file.
        """
        return {
            path: round(mean(changes))
            for path, changes in self._line_stats[0].items()
        }

    def get_total_deletions(self) -> Dict[str, int]:
        """
        Calculates total lines deleted per file.
        """
        return {
            path: sum(changes)
            for path, changes in self._line_stats[1].items()
        }

    def get_max_deletions(self) -> Dict[str, int]:
        """
        Finds maximum lines deleted in a single commit per file.
        """
        return {
            path: max(changes)
            for path, changes in self._line_stats[1].items()
        }

    def get_average_deletions(self) -> Dict[str, int]:
        """
        Calculates average lines deleted per commit per file.
        """
        return {
            path: round(mean(changes))
            for path, changes in self._line_stats[1].items()
        }
