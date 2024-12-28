"""
Classes and utilities for handling commit-related operations, including
CommitChanges, ChangeType, and CodeMethod.
"""

import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, List, Set, Dict, Tuple, Optional, Union

import hashlib
import lizard
import lizard_languages
from git import Diff, Git, NULL_TREE
from git.objects import Commit as GitCommit
from git.objects.base import IndexObject

from gitanalyzer.domain.developer import Developer

# Configure logging
logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """
    Represents different types of changes that can occur in a commit.
    Available types: ADDITION, DUPLICATE, MOVED, REMOVED, CHANGED, UNDEFINED
    """

    ADDITION = 1
    DUPLICATE = 2
    MOVED = 3
    REMOVED = 4
    CHANGED = 5
    UNDEFINED = 6


class MaintenanceMetric(Enum):
    """
    Defines the key metrics used in the Delta Maintenance Model for code analysis.
    """

    METHOD_SIZE = 1
    METHOD_COMPLEXITY = 2
    METHOD_INTERFACE = 3


class CodeMethod:
    """
    Represents a code method/function with its associated metrics and properties.
    Analyzes and stores various code quality metrics using Lizard.
    """

    # Risk thresholds for maintenance metrics
    SIZE_THRESHOLD = 15
    COMPLEXITY_THRESHOLD = 5
    INTERFACE_THRESHOLD = 2

    def __init__(self, function: Any) -> None:
        """
        Initialize a CodeMethod instance using Lizard's analysis results.
        Extracts and stores various metrics about the method.
        """
        self.method_name: str = function.name
        self.full_name: str = function.long_name
        self.source_file: str = function.filename
        self.code_lines: int = function.nloc
        self.cyclomatic_complexity: int = function.cyclomatic_complexity
        self.token_count: int = function.token_count
        self.args: List[str] = function.parameters
        self.line_start: int = function.start_line
        self.line_end: int = function.end_line
        self.incoming_calls: int = function.fan_in
        self.outgoing_calls: int = function.fan_out
        self.total_outgoing_calls: int = function.general_fan_out
        self.total_lines: int = function.length
        self.max_nesting: int = function.top_nesting_level

    def __eq__(self, other) -> bool:
        """
        Compare two methods for equality based on name and parameters.
        """
        return self.method_name == other.method_name and self.args == other.args

    def __hash__(self) -> int:
        """
        Generate a unique hash for the method based on name and parameters.
        """
        return hash((
            "method_name", self.method_name,
            "full_name", self.full_name,
            "args", tuple(self.args)
        ))

    def check_risk_level(self, metric: MaintenanceMetric) -> bool:
        """
        Determine if the method is low-risk according to the specified metric.

        Args:
            metric: The maintenance metric to evaluate

        Returns:
            bool: True if the method is considered low-risk for the given metric
        """
        if metric is MaintenanceMetric.METHOD_SIZE:
            return self.code_lines <= self.SIZE_THRESHOLD
        if metric is MaintenanceMetric.METHOD_COMPLEXITY:
            return self.cyclomatic_complexity <= self.COMPLEXITY_THRESHOLD
        assert metric is MaintenanceMetric.METHOD_INTERFACE
        return len(self.args) <= self.INTERFACE_THRESHOLD


class FileChange:
    """
    Represents a file that has been modified within a commit, tracking its
    changes and metrics.
    """

    def __init__(self, diff_object: Diff):
        """
        Creates a new FileChange instance to track modifications to a file.
        
        Args:
            diff_object: Git diff object containing change information
        """
        self._diff = diff_object
        
        # Lazy-loaded properties
        self._cached_nloc = None
        self._cached_complexity = None
        self._cached_tokens = None
        self._methods_current: List[CodeMethod] = []
        self._methods_previous: List[CodeMethod] = []

    def __hash__(self) -> int:
        """
        Generates a unique hash for the file change using SHA-256,
        based on the change type, path, and content.
        """
        hash_input = f"{self.modification_type.name} {self.new_path} {self.content!r}"
        return hash(hashlib.sha256(hash_input.encode("utf-8")).hexdigest())

    @property
    def modification_type(self) -> ChangeType:
        return self._determine_change_type(self._diff)

    @staticmethod
    def _determine_change_type(diff: Diff) -> ChangeType:
        """
        Determines the type of change made to the file.
        """
        if diff.new_file:
            return ChangeType.ADDITION
        if diff.deleted_file:
            return ChangeType.REMOVED
        if diff.renamed_file:
            return ChangeType.MOVED
        if diff.a_blob and diff.b_blob and diff.a_blob != diff.b_blob:
            return ChangeType.CHANGED
        return ChangeType.UNDEFINED

    @property
    def diff_text(self) -> str:
        """
        Returns the diff text in UTF-8 format.
        """
        return self._decode_text(self._diff.diff) or ''

    def _decode_text(self, content: Union[str, bytes, None]) -> Optional[str]:
        """
        Safely decodes content to UTF-8 string format.
        """
        try:
            if isinstance(content, bytes):
                return content.decode("utf-8", "ignore")
            if isinstance(content, str):
                return content
            return None
        except (AttributeError, ValueError):
            logger.debug(f"Failed to decode diff for file {self.filename}")
            return None

    @property
    def content(self) -> Optional[bytes]:
        """
        Returns the current file content in raw bytes.
        """
        return self._get_raw_content(self._diff.b_blob)

    @property
    def previous_content(self) -> Optional[bytes]:
        """
        Returns the previous version's content in raw bytes.
        """
        return self._get_raw_content(self._diff.a_blob)

    def _get_raw_content(self, blob: Optional[IndexObject]) -> Optional[bytes]:
        """
        Extracts raw content from a git blob object.
        """
        return blob.data_stream.read() if blob is not None else None

    @property
    def current_code(self) -> Optional[str]:
        """
        Returns the current version's source code as text.
        """
        if self.content and isinstance(self.content, bytes):
            return self._decode_text(self.content)
        return None

    @property
    def previous_code(self) -> Optional[str]:
        """
        Returns the previous version's source code as text.
        """
        if self.previous_content and isinstance(self.previous_content, bytes):
            return self._decode_text(self.previous_content)
        return None

    @property
    def lines_added(self) -> int:
        """
        Counts the number of lines added in this change.
        """
        return sum(1 for line in self.diff_text.replace("\r", "").split("\n")
                  if line.startswith("+") and not line.startswith("+++"))

    @property
    def lines_removed(self) -> int:
        """
        Counts the number of lines removed in this change.
        """
        return sum(1 for line in self.diff_text.replace("\r", "").split("\n")
                  if line.startswith("-") and not line.startswith("---"))
    
    @property
    def original_path(self) -> Optional[str]:
        """
        Gets the file's original path before changes.
        Returns None for newly added files.
        """
        if self._diff.a_path:
            return str(Path(self._diff.a_path))
        return None

    @property
    def current_path(self) -> Optional[str]:
        """
        Gets the file's current path after changes.
        Returns None for deleted files.
        """
        if self._diff.b_path:
            return str(Path(self._diff.b_path))
        return None

    @property
    def filename(self) -> str:
        """
        Extracts the base filename from the path.
        Uses current path if available, falls back to original path.
        """
        path = self.current_path if (self.current_path and self.current_path != "/dev/null") else self.original_path
        assert path, "At least one path must exist"
        return Path(path).name

    @property
    def is_analyzable(self) -> bool:
        """
        Checks if the file's language is supported for analysis.
        Uses Lizard's language detection based on file extension.
        """
        return lizard_languages.get_reader_for(self.filename) is not None

    @property
    def lines_of_code(self) -> Optional[int]:
        """
        Returns the total lines of code in the file.
        Triggers metric calculation if not already done.
        """
        self._compute_code_metrics()
        return self._cached_nloc

    @property
    def cyclomatic_complexity(self) -> Optional[int]:
        """
        Returns the file's cyclomatic complexity score.
        Triggers metric calculation if not already done.
        """
        self._compute_code_metrics()
        return self._cached_complexity

    @property
    def token_count(self) -> Optional[int]:
        """
        Returns the total count of tokens in the file.
        Triggers metric calculation if not already done.
        """
        self._compute_code_metrics()
        return self._cached_tokens

    @property
    def parsed_diff(self) -> Dict[str, List[Tuple[int, str]]]:
        """
        Parses the diff into a structured format showing added and deleted lines.
        
        Returns:
            Dictionary with keys 'added' and 'deleted', each containing a list of
            tuples (line_number, line_content)
        """
        diff_lines = self.diff_text.split("\n")
        changes = {
            "added": [],
            "deleted": [],
        }

        deletion_counter = addition_counter = 0

        for line in diff_lines:
            line = line.rstrip()
            deletion_counter += 1
            addition_counter += 1

            if line.startswith("@@"):
                deletion_counter, addition_counter = self._parse_chunk_header(line)
                continue

            if line.startswith("-"):
                changes["deleted"].append((deletion_counter, line[1:]))
                addition_counter -= 1
            elif line.startswith("+"):
                changes["added"].append((addition_counter, line[1:]))
                deletion_counter -= 1
            elif line == r"\ No newline at end of file":
                deletion_counter -= 1
                addition_counter -= 1

        return changes
    
    @staticmethod
    def _parse_chunk_header(line: str) -> Tuple[int, int]:
        """
        Extracts line numbers from a git diff chunk header.
        
        Args:
            line: Diff chunk header line starting with @@
            
        Returns:
            Tuple of (deletion_start, addition_start) line numbers
        """
        chunks = line.split(" ")
        old_file_info = chunks[1]
        new_file_info = chunks[2]
        
        deletion_start = int(old_file_info.split(",")[0].replace("-", "")) - 1
        addition_start = int(new_file_info.split(",")[0]) - 1
        
        return deletion_start, addition_start

    @property
    def current_methods(self) -> List[CodeMethod]:
        """
        Analyzes and returns all methods in the current version of the file.
        Includes metrics like complexity, size, and parameters.
        """
        self._compute_code_metrics()
        return self._methods_current

    @property
    def previous_methods(self) -> List[CodeMethod]:
        """
        Analyzes and returns all methods from the previous version of the file.
        Includes complete method information before changes.
        """
        self._compute_code_metrics(analyze_previous=True)
        return self._methods_previous

    @property
    def modified_methods(self) -> List[CodeMethod]:
        """
        Identifies and returns methods that were modified in this change.
        Compares both versions of the file to detect changes accurately.
        """
        current = self.current_methods
        previous = self.previous_methods
        additions = self.parsed_diff["added"]
        deletions = self.parsed_diff["deleted"]

        # Find methods affected by additions
        changed_in_current = {
            method for line_num, _ in additions
            for method in current
            if method.line_start <= line_num <= method.line_end
        }

        # Find methods affected by deletions
        changed_in_previous = {
            method for line_num, _ in deletions
            for method in previous
            if method.line_start <= line_num <= method.line_end
        }

        return list(changed_in_current.union(changed_in_previous))

    @staticmethod
    def _calculate_risk_profile(
            methods: List[CodeMethod],
            metric: MaintenanceMetric
    ) -> Tuple[int, int]:
        """
        Calculates the risk distribution for a set of methods.
        
        Args:
            methods: List of methods to analyze
            metric: Maintenance metric to evaluate risk
            
        Returns:
            Tuple of (low_risk_volume, high_risk_volume) in lines of code
        """
        low_risk = sum(m.code_lines for m in methods if m.check_risk_level(metric))
        high_risk = sum(m.code_lines for m in methods if not m.check_risk_level(metric))
        return low_risk, high_risk

    def _compute_risk_delta(self, metric: MaintenanceMetric) -> Tuple[int, int]:
        """
        Calculates how the risk profile changed between versions.
        
        Args:
            metric: Maintenance metric to evaluate
            
        Returns:
            Tuple of (low_risk_change, high_risk_change) in lines of code
        """
        assert self.is_analyzable
        
        # Calculate risk profiles for both versions
        prev_low, prev_high = self._calculate_risk_profile(
            self.previous_methods, metric
        )
        curr_low, curr_high = self._calculate_risk_profile(
            self.current_methods, metric
        )
        
        # Return the changes in each risk category
        return (curr_low - prev_low, curr_high - prev_high)
    
    def _compute_code_metrics(self, analyze_previous: bool = False) -> None:
        """
        Analyzes code metrics using Lizard for current and optionally previous versions.
        
        Args:
            analyze_previous: Whether to analyze the previous version of the code
        """
        if not self.is_analyzable:
            return

        # Analyze current version if not already done
        if self.current_code and self._cached_nloc is None:
            metrics = lizard.analyze_file.analyze_source_code(
                self.filename, 
                self.current_code
            )
            
            # Store basic metrics
            self._cached_nloc = metrics.nloc
            self._cached_complexity = metrics.CCN
            self._cached_tokens = metrics.token_count
            
            # Process methods
            self._methods_current = [CodeMethod(func) for func in metrics.function_list]

        # Analyze previous version if requested
        if (analyze_previous and 
            self.previous_code and 
            not self._methods_previous):
            
            previous_metrics = lizard.analyze_file.analyze_source_code(
                self.filename,
                self.previous_code
            )
            
            self._methods_previous = [CodeMethod(func) for func in previous_metrics.function_list]

    def _decode_content(self, content: bytes) -> Optional[str]:
        """
        Attempts to decode binary content to UTF-8 string.
        
        Args:
            content: Binary content to decode
            
        Returns:
            Decoded string or None if decoding fails
        """
        try:
            return content.decode("utf-8", "ignore")
        except (AttributeError, ValueError):
            logger.debug("Failed to decode content for file %s", self.filename)
            return None

    def __eq__(self, other: object) -> bool:
        """
        Checks equality between two FileChange objects.
        """
        if not isinstance(other, FileChange):
            return NotImplemented
        if self is other:
            return True
        return self.__dict__ == other.__dict__


class CommitInfo:
    """
    Represents a Git commit with its associated metadata and changes.
    Provides access to commit details like hash, author, dates, and modified files.
    """

    def __init__(self, git_commit: GitCommit, config) -> None:
        """
        Creates a new CommitInfo instance.
        
        Args:
            git_commit: GitPython commit object
            config: Analysis configuration settings
        """
        self._commit = git_commit
        self._config = config
        self._cached_stats = None

    def __hash__(self) -> int:
        """
        Generates a hash based on the commit's SHA.
        Uses the commit's hexadecimal SHA to ensure uniqueness.
        """
        return hash(self._commit.hexsha)

    @property
    def sha(self) -> str:
        """
        Returns the commit's SHA identifier.
        """
        return self._commit.hexsha

    @property
    def author(self) -> Developer:
        """
        Returns the primary author of the commit.
        """
        return self._config.get("developer_factory").get_developer(
            self._commit.author.name,
            self._commit.author.email
        )

    @property
    def collaborators(self) -> List[Developer]:
        """
        Returns all additional contributors to the commit.
        """
        contributors = []
        for collaborator in self._commit.co_authors:
            dev = self._config.get("developer_factory").get_developer(
                collaborator.name,
                collaborator.email
            )
            contributors.append(dev)
        
        return contributors
    
    @property
    def code_reviewer(self) -> Developer:
        """
        Returns the developer who reviewed and committed the changes.
        """
        return self._config.get("developer_factory").get_developer(
            self._commit.committer.name,
            self._commit.committer.email
        )

    @property
    def repository_name(self) -> str:
        """
        Returns the name of the Git repository.
        """
        return Path(self._config.get("path_to_repo")).name

    @property
    def repository_path(self) -> str:
        """
        Returns the full filesystem path to the repository.
        """
        return str(Path(self._config.get("path_to_repo")))

    @property
    def creation_date(self) -> datetime:
        """
        Returns when the changes were originally authored.
        """
        return self._commit.authored_datetime

    @property
    def commit_date(self) -> datetime:
        """
        Returns when the changes were committed to the repository.
        """
        return self._commit.committed_datetime

    @property
    def author_timezone_offset(self) -> int:
        """
        Returns the author's timezone offset in seconds from UTC.
        """
        return int(self._commit.author_tz_offset)

    @property
    def commit_timezone_offset(self) -> int:
        """
        Returns the committer's timezone offset in seconds from UTC.
        """
        return int(self._commit.committer_tz_offset)

    @property
    def message(self) -> str:
        """
        Returns the commit's description message.
        """
        return str(self._commit.message.strip())

    @property
    def parent_commits(self) -> List[str]:
        """
        Returns list of parent commit SHAs.
        """
        return [parent.hexsha for parent in self._commit.parents]

    @property
    def is_merge(self) -> bool:
        """
        Indicates if this is a merge commit.
        """
        return len(self._commit.parents) > 1

    def _compute_stats(self):
        """
        Calculates commit statistics if not already cached.
        """
        if self._cached_stats is not None:
            return self._cached_stats

        if not self.parent_commits:
            # For commits without parents (initial commits)
            raw_stats = self._config.get('git').repo.git.diff_tree(
                self.sha, 
                "--", 
                numstat=True, 
                root=True
            )
            
            # Process the output, skipping the first line
            processed_stats = ""
            for line in raw_stats.splitlines()[1:]:
                adds, dels, fname = line.split("\t")
                processed_stats += f"{adds}\t{dels}\t{fname}\n"
            
        else:
            # For normal commits
            processed_stats = self._config.get('git').repo.git.diff(
                self._commit.parents[0].hexsha,
                self._commit.hexsha,
                "--",
                numstat=True,
                root=True
            )

        self._cached_stats = self._parse_git_stats(processed_stats)
        return self._cached_stats

    def _parse_git_stats(self, stats_text: str) -> dict:
        """
        Parses git diff statistics into a structured format.
        
        Args:
            stats_text: Raw git diff stats output
            
        Returns:
            Dictionary containing parsed statistics
        """
        summary = {
            "insertions": 0,
            "deletions": 0,
            "lines": 0,
            "files": 0
        }

        for line in stats_text.splitlines():
            additions_raw, deletions_raw, _ = line.split("\t")
            
            # Convert "-" to 0 for binary files
            additions = 0 if additions_raw == "-" else int(additions_raw)
            deletions = 0 if deletions_raw == "-" else int(deletions_raw)
            
            summary["insertions"] += additions
            summary["deletions"] += deletions
            summary["lines"] += additions + deletions
            summary["files"] += 1

        return summary
    
    @property
    def added_lines(self) -> int:
        """
        Returns the total number of lines added in this commit.
        """
        return self._compute_stats()["insertions"]

    @property
    def removed_lines(self) -> int:
        """
        Returns the total number of lines removed in this commit.
        """
        return self._compute_stats()["deletions"]

    @property
    def total_changes(self) -> int:
        """
        Returns the total number of line changes (additions + deletions).
        """
        return self._compute_stats()["lines"]

    @property
    def changed_files(self) -> int:
        """
        Returns the number of files modified in this commit.
        """
        return self._compute_stats()["files"]

    @property
    def file_changes(self) -> List[FileChange]:
        """
        Returns a list of all file changes in this commit.
        Note: For merge commits, an empty list is returned due to complexity
        of parsing merge conflicts. See:
        - https://haacked.com/archive/2014/02/21/reviewing-merge-commits/
        - https://github.com/ishepard/pydriller/issues/89#issuecomment-590243707
        """
        diff_options = {}
        
        # Apply configuration options
        if self._config.get("histogram"):
            diff_options["histogram"] = True
        if self._config.get("skip_whitespaces"):
            diff_options["w"] = True

        # Handle different commit scenarios
        if len(self.parent_commits) == 1:
            # Normal commit with one parent
            diff_data: Any = self._commit.parents[0].diff(
                other=self._commit,
                paths=None,
                create_patch=True,
                **diff_options
            )
        elif len(self.parent_commits) > 1:
            # Merge commit - return empty list
            # TODO: Implement parsing of combined diff output for merge conflicts
            diff_data = []
        else:
            # Initial commit - compare with empty tree
            diff_data = self._commit.diff(
                NULL_TREE,
                paths=None,
                create_patch=True,
                **diff_options
            )

        return self._process_diff_data(diff_data)

    def _process_diff_data(self, diff_data: List[Diff]) -> List[FileChange]:
        """
        Processes raw git diff data into FileChange objects.
        
        Args:
            diff_data: List of git diff objects
            
        Returns:
            List of FileChange objects representing the modifications
        """
        return [FileChange(diff=diff) for diff in diff_data]

    @property
    def is_in_main_branch(self) -> bool:
        """
        Indicates whether this commit is part of the main branch.
        """
        return self._config.get("main_branch") in self.containing_branches

    @property
    def containing_branches(self) -> Set[str]:
        """
        Returns all branches that contain this commit.
        """
        git = Git(str(self._config.get("path_to_repo")))
        branch_set = set()
        
        # Prepare branch lookup arguments
        lookup_args = ["--contains", self.sha]
        
        # Add optional flags based on configuration
        if self._config.get("include_remotes"):
            lookup_args.insert(0, "-r")
        if self._config.get("include_refs"):
            lookup_args.insert(0, "-a")
            
        # Process branch command output
        for branch in set(git.branch(*lookup_args).split("\n")):
            cleaned_branch = branch.strip().replace("* ", "")
            branch_set.add(cleaned_branch)
            
        return branch_set
    
    @property
    def maintainability_size_metric(self) -> Optional[float]:
        """
        Calculates the maintainability metric for method sizes.
        
        Returns a value between 0.0 and 1.0 indicating the proportion of positive
        maintainability changes. Higher values (closer to 1.0) indicate improvements
        like splitting large methods or working on small methods. Lower values
        indicate work on methods that remain or become too large.
        """
        return self._calculate_maintainability_score(MaintenanceMetric.METHOD_SIZE)

    @property
    def maintainability_complexity_metric(self) -> Optional[float]:
        """
        Calculates the maintainability metric for method complexity.
        
        Returns a value between 0.0 and 1.0 indicating the proportion of positive
        maintainability changes. Higher values indicate improvements like reducing
        method complexity, while lower values indicate work on methods that remain
        or become more complex.
        """
        return self._calculate_maintainability_score(MaintenanceMetric.METHOD_COMPLEXITY)

    @property
    def maintainability_interface_metric(self) -> Optional[float]:
        """
        Calculates the maintainability metric for method interfaces.
        
        Returns a value between 0.0 and 1.0 indicating the proportion of positive
        maintainability changes. Higher values indicate improvements like reducing
        parameter counts, while lower values indicate work on methods that maintain
        or increase large parameter lists.
        """
        return self._calculate_maintainability_score(MaintenanceMetric.METHOD_INTERFACE)

    def _calculate_maintainability_score(self, metric: MaintenanceMetric) -> Optional[float]:
        """
        Computes a maintainability score based on the given metric.
        
        Evaluates changes as either positive (adding low-risk or removing high-risk code)
        or negative (adding high-risk or removing low-risk code).
        
        Args:
            metric: The maintenance metric to evaluate
            
        Returns:
            Float between 0.0 and 1.0 representing the proportion of positive changes,
            or None if no supported files were modified
        """
        risk_changes = self._calculate_risk_changes(metric)
        if risk_changes:
            low_risk_delta, high_risk_delta = risk_changes
            return self._calculate_improvement_ratio(low_risk_delta, high_risk_delta)
        return None

    def _calculate_risk_changes(
            self, metric: MaintenanceMetric
    ) -> Optional[Tuple[int, int]]:
        """
        Analyzes how the risk profile changed in this commit.
        
        Args:
            metric: The maintenance metric to evaluate
            
        Returns:
            Tuple of (low_risk_change, high_risk_change) in lines of code,
            or None if no supported files were modified
        """
        analyzable_files = [
            file for file in self.file_changes 
            if file.is_analyzable
        ]
        
        if analyzable_files:
            changes = [
                file._compute_risk_delta(metric)
                for file in analyzable_files
            ]
            
            total_low_risk = sum(low for low, _ in changes)
            total_high_risk = sum(high for _, high in changes)
            
            return total_low_risk, total_high_risk
        return None

    @staticmethod
    def _calculate_improvement_ratio(
            low_risk_change: int,
            high_risk_change: int
    ) -> Optional[float]:
        """
        Calculates the ratio of positive maintenance changes to total changes.
        
        Args:
            low_risk_change: Net change in low-risk code
            high_risk_change: Net change in high-risk code
            
        Returns:
            Ratio of positive changes (0.0 to 1.0), or None if no changes
        """
        positive_changes = negative_changes = 0

        # Evaluate low risk changes
        if low_risk_change >= 0:
            positive_changes = low_risk_change
        else:
            negative_changes = abs(low_risk_change)

        # Evaluate high risk changes
        if high_risk_change >= 0:
            negative_changes += high_risk_change
        else:
            positive_changes += abs(high_risk_change)

        assert positive_changes >= 0 and negative_changes >= 0
        
        total_changes = positive_changes + negative_changes
        if total_changes == 0:
            return None
            
        improvement_ratio = positive_changes / total_changes
        assert 0.0 <= improvement_ratio <= 1.0
        
        return improvement_ratio

    def __eq__(self, other: object) -> bool:
        """
        Checks if two CommitInfo objects are equal.
        """
        if not isinstance(other, CommitInfo):
            return NotImplemented
        if self is other:
            return True
        return self.__dict__ == other.__dict__