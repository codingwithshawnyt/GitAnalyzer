"""
This module implements the History Complexity Period Factor (HCPF) calculation,
which is a component of the History Complexity Metric (HCM).

To calculate the complete HCM, you need to:
1. Calculate HCPF for each period of interest
2. Sum all HCPF values

Example usage:
    period1_hcpf = FileHistoryMetric(..., start=commit1, end=commit2).calculate()
    period2_hcpf = FileHistoryMetric(..., start=commit3, end=commit4).calculate()
    
    total_hcm = period1_hcpf + period2_hcpf

Reference implementation based on:
https://github.com/codingwithshawnyt/GitAnalyzer
"""

from math import log
from gitanalyzer.repository import ChangeType
from gitanalyzer.metrics.process.base_metric import BaseProcessMetric


class FileHistoryMetric(BaseProcessMetric):
    """
    Calculates the historical complexity of file changes within a repository.
    This metric evaluates how changes are distributed across files during
    a specific time period, considering both the frequency and magnitude
    of modifications.
    """

    def calculate(self):
        """
        Analyzes the repository history to compute the complexity factor
        for each modified file between the specified commits.

        Returns:
            dict: Mapping of file paths to their complexity scores (0-100)
            {
                'path/to/file': float,
                ...
            }
        """
        file_changes = {}
        path_mappings = {}
        
        for commit in self.repository.iter_commits():
            for change in commit.file_changes:
                current_path = path_mappings.get(
                    change.new_path, 
                    change.new_path
                )

                if change.change_type == ChangeType.RENAMED:
                    path_mappings[change.old_path] = current_path

                change_size = change.lines_added + change.lines_removed
                if change_size > 0:
                    file_changes[current_path] = (
                        file_changes.get(current_path, 0) + change_size
                    )

        total_change_volume = sum(file_changes.values())
        modified_file_count = len(file_changes)

        # Convert absolute changes to relative proportions
        for filepath in file_changes:
            file_changes[filepath] = file_changes[filepath] / total_change_volume

        # Calculate normalized entropy
        normalized_entropy = 0
        if modified_file_count > 1:
            normalized_entropy = -sum(
                p * log(p + 1e-10, modified_file_count) 
                for p in file_changes.values()
            )

        # Compute final complexity scores
        result = {}
        for filepath in file_changes:
            complexity = file_changes[filepath] * normalized_entropy
            result[filepath] = round(complexity * 100, 2)

        return result
