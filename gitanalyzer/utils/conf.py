"""
Module for managing configuration settings in GitAnalyzer.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import pytz
from gitdb.exc import BadName

from gitanalyzer.domain.commit import Commit
from gitanalyzer.utils.developer import BasicDeveloperFactory, MappedDeveloperFactory

# Configure logging
logger = logging.getLogger(__name__)


class ConfigurationManager:
    """
    Manages the configuration settings for repository analysis.
    
    This class handles all configuration parameters for the repository analysis process,
    including date ranges, branch specifications, and filtering options. It ensures
    the validity of configuration combinations and provides methods to access and
    modify settings.
    """

    def __init__(self, config_params: Dict[str, Any]) -> None:
        # Store configuration parameters
        self._settings = config_params.copy()

        # Validate and process repository paths
        self._validate_repository_paths(self._settings.get('path_to_repo'))
        self._process_repository_paths()

        # Set up developer factory based on mailmap configuration
        self._initialize_developer_factory()

    def _validate_repository_paths(self, repo_path: Union[str, List[str]]) -> None:
        """
        Validates that repository path(s) are properly formatted.
        
        Args:
            repo_path: Single path string or list of path strings
        
        Raises:
            Exception: If repo_path is neither a string nor a list
        """
        if not isinstance(repo_path, (str, list)):
            raise Exception("Repository path must be either a string or list of strings")

    def _process_repository_paths(self) -> None:
        """Standardizes repository path storage to list format."""
        path = self._settings.get('path_to_repo')
        if isinstance(path, str):
            self.update_setting('path_to_repos', [path])
        else:
            self.update_setting('path_to_repos', path)

    def _initialize_developer_factory(self) -> None:
        """Sets up appropriate developer factory based on mailmap settings."""
        if self._settings.get("use_mailmap"):
            self.update_setting("developer_factory", MappedDeveloperFactory(self))
        else:
            self.update_setting("developer_factory", BasicDeveloperFactory())

    def update_setting(self, key: str, value: Any) -> None:
        """
        Updates a configuration setting.

        Args:
            key: Setting name
            value: Setting value
        """
        self._settings[key] = value

    def get_setting(self, key: str) -> Any:
        """
        Retrieves a configuration setting.

        Args:
            key: Setting name

        Returns:
            Setting value or None if not found
        """
        return self._settings.get(key)

    def validate_filters(self) -> None:
        """
        Performs comprehensive validation of all filter settings.
        """
        self._validate_filter_order()
        self._validate_from_filters()
        self._validate_to_filters()
        self._validate_timezone_settings()
        self._handle_duplicate_commit_range()

    def _validate_from_filters(self) -> None:
        """Ensures only one 'from' type filter is specified."""
        from_filters = [
            self.get_setting('since'),
            self.get_setting('since_as_filter'),
            self.get_setting('from_commit'),
            self.get_setting('from_tag')
        ]
        if not self._has_single_filter(from_filters):
            raise Exception('Only one filter allowed: since, since_as_filter, from_tag, or from_commit')

    def _validate_to_filters(self) -> None:
        """Ensures only one 'to' type filter is specified."""
        to_filters = [
            self.get_setting('to'),
            self.get_setting('to_commit'),
            self.get_setting('to_tag')
        ]
        if not self._has_single_filter(to_filters):
            raise Exception('Only one filter allowed: to, to_tag, or to_commit')

    def _handle_duplicate_commit_range(self) -> None:
        """Converts identical from/to commits to single commit filter."""
        from_commit = self.get_setting("from_commit")
        to_commit = self.get_setting("to_commit")
        
        if from_commit and to_commit and from_commit == to_commit:
            logger.warning("Converting identical from/to commits to 'single' filter")
            self.update_setting("single", to_commit)
            self.update_setting("from_commit", None)
            self.update_setting("to_commit", None)

    def _validate_filter_order(self) -> None:
        """Ensures chronological order of commit filters."""
        if self.get_setting('from_commit') and self.get_setting('to_commit'):
            git = self.get_setting('git')
            from_commit = git.get_commit(self.get_setting('from_commit'))
            to_commit = git.get_commit(self.get_setting('to_commit'))
            
            if not self._is_chronological_order(from_commit, to_commit):
                self._swap_commit_filters()

    @staticmethod
    def _is_chronological_order(first: Commit, second: Commit) -> bool:
        """
        Checks if commits are in chronological order.
        
        Args:
            first: Earlier commit
            second: Later commit
            
        Returns:
            bool: True if commits are in chronological order
        """
        if first.committer_date < second.committer_date:
            return True
        if first.committer_date == second.committer_date:
            return first.author_date < second.author_date
        return False

    def _swap_commit_filters(self) -> None:
        """Swaps from_commit and to_commit filter values."""
        from_commit = self.get_setting('from_commit')
        to_commit = self.get_setting('to_commit')
        self.update_setting('from_commit', to_commit)
        self.update_setting('to_commit', from_commit)

    @staticmethod
    def _has_single_filter(filters: List[Any]) -> bool:
        """
        Checks if at most one filter is active.
        
        Args:
            filters: List of filter values
            
        Returns:
            bool: True if one or zero filters are active
        """
        return len([f for f in filters if f is not None]) <= 1

    def get_start_commit(self) -> Optional[List[str]]:
        """
        Determines the starting commit for analysis.
        
        Returns:
            Optional[List[str]]: Git revision arguments for starting point
        """
        from_tag = self.get_setting('from_tag')
        from_commit = self.get_setting('from_commit')
        
        if from_tag:
            from_commit = self.get_setting("git").get_commit_from_tag(from_tag).hash
            
        if from_commit:
            try:
                commit = self.get_setting("git").get_commit(from_commit)
                return self._build_ancestry_path_args(commit)
            except Exception as e:
                raise Exception(f"Invalid from_tag/from_commit: {from_commit}") from e
        return None

    def _build_ancestry_path_args(self, commit: Commit) -> List[str]:
        """
        Builds git ancestry path arguments for a commit.
        
        Args:
            commit: Commit object
            
        Returns:
            List[str]: Git revision arguments
        """
        base_arg = f'--ancestry-path={commit.hash}'
        if not commit.parents:
            return [base_arg]
        if len(commit.parents) == 1:
            return [base_arg, f'^{commit.hash}^']
        return [base_arg] + [f'^{parent}' for parent in commit.parents]

    def get_end_commit(self) -> Optional[str]:
        """
        Determines the ending commit for analysis.
        
        Returns:
            Optional[str]: Ending commit hash
        """
        to_tag = self.get_setting('to_tag')
        to_commit = self.get_setting('to_commit')
        
        if to_tag:
            to_commit = self.get_setting("git").get_commit_from_tag(to_tag).hash
            
        if to_commit:
            try:
                return self.get_setting("git").get_commit(to_commit).hash
            except Exception as e:
                raise Exception(f"Invalid to_tag/to_commit: {to_commit}") from e
        return None

    def build_revision_args(self) -> Tuple[Union[str, List[str]], Dict[str, Any]]:
        """
        Constructs git revision list arguments based on configuration.
        
        Returns:
            Tuple[Union[str, List[str]], Dict[str, Any]]: Revision arguments and options
        """
        revision = self._determine_revision()
        options = self._build_revision_options()
        return revision, options

    def _determine_revision(self) -> Union[str, List[str]]:
        """
        Determines the appropriate revision specification.
        
        Returns:
            Union[str, List[str]]: Revision specification
        """
        if self.get_setting('single'):
            return [self.get_setting('single'), '-n', '1']
            
        start = self.get_start_commit()
        end = self.get_end_commit()
        
        if start or end:
            return self._build_commit_range(start, end)
            
        return self.get_setting('only_in_branch') or 'HEAD'

    def _build_commit_range(self, start: Optional[List[str]], end: Optional[str]) -> Union[str, List[str]]:
        """
        Builds commit range specification.
        
        Args:
            start: Starting commit arguments
            end: Ending commit hash
            
        Returns:
            Union[str, List[str]]: Commit range specification
        """
        if start and end:
            return [*start, end]
        if start:
            return [*start, 'HEAD']
        return end

    def _build_revision_options(self) -> Dict[str, Any]:
        """
        Builds options dictionary for git revision list.
        
        Returns:
            Dict[str, Any]: Revision options
        """
        options = {}
        
        # Handle ordering
        order = self.get_setting('order')
        if not order:
            options['reverse'] = True
        elif order == 'reverse':
            options['reverse'] = False
        elif order in ('date-order', 'author-date-order', 'topo-order'):
            options[order] = True

        # Add other options
        self._add_boolean_options(options)
        self._add_filter_options(options)
        
        return options

    def _add_boolean_options(self, options: Dict[str, Any]) -> None:
        """
        Adds boolean options to the options dictionary.
        
        Args:
            options: Options dictionary to modify
        """
        if self.get_setting('only_no_merge'):
            options['no-merges'] = True
        if self.get_setting('include_refs'):
            options['all'] = True
        if self.get_setting('include_remotes'):
            options['remotes'] = True

    def _add_filter_options(self, options: Dict[str, Any]) -> None:
        """
        Adds filter options to the options dictionary.
        
        Args:
            options: Options dictionary to modify
        """
        filter_mappings = {
            'only_authors': 'author',
            'since': 'since',
            'since_as_filter': 'since_as_filter',
            'to': 'until'
        }
        
        for setting, option in filter_mappings.items():
            value = self.get_setting(setting)
            if value is not None:
                options[option] = value

    def should_filter_commit(self, commit: Commit) -> bool:
        """
        Determines if a commit should be filtered out.
        
        Args:
            commit: Commit to evaluate
            
        Returns:
            bool: True if commit should be filtered out
        """
        if self._should_filter_by_file_type(commit):
            return True
            
        filter_sets = {
            'only_commits': commit.hash,
            'filepath_commits': commit.hash,
            'tagged_commits': commit.hash
        }
        
        return any(
            self.get_setting(filter_set) is not None and
            commit_value not in self.get_setting(filter_set)
            for filter_set, commit_value in filter_sets.items()
        )

    def _should_filter_by_file_type(self, commit: Commit) -> bool:
        """
        Checks if commit should be filtered based on file types.
        
        Args:
            commit: Commit to check
            
        Returns:
            bool: True if commit should be filtered
        """
        file_types = self.get_setting('only_modifications_with_file_types')
        if not file_types:
            return False
            
        return not any(
            mod.filename.endswith(tuple(file_types))
            for mod in commit.modified_files
        )

    def _validate_timezone_settings(self) -> None:
        """Ensures all datetime settings have proper timezone information."""
        for setting in ('since', 'since_as_filter', 'to'):
            value = self.get_setting(setting)
            if value is not None:
                self.update_setting(setting, self._ensure_timezone(value))

    @staticmethod
    def _ensure_timezone(dt: datetime) -> datetime:
        """
        Ensures datetime has timezone information.
        
        Args:
            dt: Datetime to check
            
        Returns:
            datetime: Datetime with timezone information
        """
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            return dt.replace(tzinfo=pytz.utc)
        return dt

    @staticmethod
    def _compare_commit_dates(first_commit: Commit, second_commit: Commit) -> bool:
        """
        Compares two commits chronologically based on committer and author dates.
        
        Args:
            first_commit: First commit to compare
            second_commit: Second commit to compare
            
        Returns:
            bool: True if first_commit is chronologically before second_commit
        """
        if first_commit.committer_date < second_commit.committer_date:
            return True
        if first_commit.committer_date == second_commit.committer_date:
            return first_commit.author_date < second_commit.author_date
        return False

    def resolve_start_commit(self) -> Optional[List[str]]:
        """
        Resolves the starting commit based on from_commit or from_tag filters.
        
        Returns:
            Optional[List[str]]: Git revision arguments for the starting commit
        """
        tag = self.get_setting('from_tag')
        commit_hash = self.get_setting('from_commit')
        
        if tag:
            commit_hash = self.get_setting("git").get_commit_from_tag(tag).hash
            
        if not commit_hash:
            return None
            
        try:
            commit = self.get_setting("git").get_commit(commit_hash)
            return self._build_ancestry_args(commit)
        except Exception:
            raise Exception(f"Invalid commit specified in from_tag/from_commit filter: {commit_hash}")

    def _build_ancestry_args(self, commit: Commit) -> List[str]:
        """
        Constructs git ancestry path arguments for a given commit.
        
        Args:
            commit: Target commit
            
        Returns:
            List[str]: Git ancestry path arguments
        """
        base = [f'--ancestry-path={commit.hash}']
        if not commit.parents:
            return base
        if len(commit.parents) == 1:
            return base + [f'^{commit.hash}^']
        return base + [f'^{parent}' for parent in commit.parents]

    def resolve_end_commit(self) -> Optional[str]:
        """
        Resolves the ending commit based on to_commit or to_tag filters.
        
        Returns:
            Optional[str]: Hash of the ending commit
        """
        tag = self.get_setting('to_tag')
        commit_hash = self.get_setting('to_commit')
        
        if tag:
            commit_hash = self.get_setting("git").get_commit_from_tag(tag).hash
            
        if not commit_hash:
            return None
            
        try:
            return self.get_setting("git").get_commit(commit_hash).hash
        except Exception:
            raise Exception(f"Invalid commit specified in to_tag/to_commit filter: {commit_hash}")

    @staticmethod
    def has_single_active_filter(filters: List[Any]) -> bool:
        """
        Checks if list contains at most one active filter.
        
        Args:
            filters: List of filter values
            
        Returns:
            bool: True if list contains zero or one non-None values
        """
        return sum(1 for f in filters if f is not None) <= 1

    def construct_revision_args(self) -> Tuple[Union[str, List[str]], Dict[str, Any]]:
        """
        Constructs git revision list arguments based on current configuration.
        
        Returns:
            Tuple containing revision specification and additional options
        """
        revision = self._determine_revision_spec()
        options = self._build_revision_options()
        return revision, options

    def _determine_revision_spec(self) -> Union[str, List[str]]:
        """
        Determines the appropriate revision specification based on filters.
        
        Returns:
            Union[str, List[str]]: Git revision specification
        """
        if self.get_setting('single'):
            return [self.get_setting('single'), '-n', '1']
            
        start = self.resolve_start_commit()
        end = self.resolve_end_commit()
        
        if start or end:
            return self._build_revision_range(start, end)
            
        return self.get_setting('only_in_branch') or 'HEAD'

    def _build_revision_range(self, start: Optional[List[str]], end: Optional[str]) -> Union[str, List[str]]:
        """
        Constructs revision range from start and end points.
        
        Args:
            start: Starting revision arguments
            end: Ending revision
            
        Returns:
            Union[str, List[str]]: Complete revision range specification
        """
        if start and end:
            return [*start, end]
        if start:
            return [*start, 'HEAD']
        return end

    def should_exclude_commit(self, commit: Commit) -> bool:
        """
        Determines if a commit should be excluded based on filters.
        
        Args:
            commit: Commit to evaluate
            
        Returns:
            bool: True if commit should be excluded
        """
        if self._should_exclude_by_file_type(commit):
            logger.debug('Commit excluded due to file type filters')
            return True
            
        filter_checks = {
            'only_commits': ('specified commits', commit.hash),
            'filepath_commits': ('file modification', commit.hash),
            'tagged_commits': ('tag requirement', commit.hash)
        }
        
        for filter_name, (reason, value) in filter_checks.items():
            filter_set = self.get_setting(filter_name)
            if filter_set and value not in filter_set:
                logger.debug(f"Commit excluded due to {reason}")
                return True
                
        return False

    def _should_exclude_by_file_type(self, commit: Commit) -> bool:
        """
        Checks if commit should be excluded based on file type filters.
        
        Args:
            commit: Commit to check
            
        Returns:
            bool: True if commit should be excluded
        """
        allowed_types = self.get_setting('only_modifications_with_file_types')
        if not allowed_types:
            return False
            
        return not any(
            mod.filename.endswith(tuple(allowed_types))
            for mod in commit.modified_files
        )

    def ensure_timezone_consistency(self) -> None:
        """Ensures all datetime settings have consistent timezone information."""
        for setting in ('since', 'since_as_filter', 'to'):
            value = self.get_setting(setting)
            if value is not None:
                self.update_setting(setting, self._normalize_timezone(value))

    @staticmethod
    def _normalize_timezone(dt: datetime) -> datetime:
        """
        Ensures datetime has UTC timezone if none specified.
        
        Args:
            dt: Datetime to normalize
            
        Returns:
            datetime: Datetime with timezone information
        """
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            return dt.replace(tzinfo=pytz.utc)
        return dt