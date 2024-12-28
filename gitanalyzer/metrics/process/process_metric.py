"""
Base module for implementing git repository process metrics analysis.
"""

from datetime import datetime
from typing import Optional
from gitanalyzer import RepositoryAnalyzer


class BaseProcessMetric:
    """
    Base class for implementing git repository process metrics.
    All specific process metrics should inherit from this class.
    """

    def __init__(self, repository_path: str,
                 start_date: Optional[datetime] = None,
                 end_date: Optional[datetime] = None,
                 initial_commit: Optional[str] = None,
                 final_commit: Optional[str] = None):
        """
        Initialize the process metric analyzer.

        Args:
            repository_path (str): Local path to the git repository
            start_date (datetime, optional): Beginning date for analysis
            end_date (datetime, optional): End date for analysis
            initial_commit (str, optional): Starting commit hash (alternative to start_date)
            final_commit (str, optional): Ending commit hash (alternative to end_date)

        Raises:
            ValueError: If neither date-based nor commit-based range is properly specified
        """
        # Validate input parameters
        if not (start_date or initial_commit):
            raise ValueError('Must specify either start_date or initial_commit')

        if not (end_date or final_commit):
            raise ValueError('Must specify either end_date or final_commit')

        # Handle single commit analysis case
        if initial_commit and final_commit and initial_commit == final_commit:
            self.repository = RepositoryAnalyzer(
                path=repository_path,
                single_commit=initial_commit
            )
        else:
            # Initialize repository analyzer with specified range
            self.repository = RepositoryAnalyzer(
                path=repository_path,
                start_date=start_date,
                end_date=end_date,
                start_commit=initial_commit,
                end_commit=final_commit,
                traverse_order='reverse'
            )

    def compute(self) -> int:
        """
        Calculate the metric value.
        To be implemented by specific metric classes.

        Returns:
            int: Computed metric value
        """
        return 0
