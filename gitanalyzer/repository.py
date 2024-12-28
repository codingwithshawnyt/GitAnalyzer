"""
Core module containing the GitRepo class, which serves as the primary interface for GitAnalyzer.
"""

import os
import math
import logging
import tempfile
import shutil
from typing import List, Generator, Optional, Union
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
import concurrent.futures

from git import Repo

from gitanalyzer.domain.commit import Commit
from gitanalyzer.git import GitHandler
from gitanalyzer.utils.config import Configuration

# Configure logging
logger = logging.getLogger(__name__)

class GitRepo:
    """
    Primary class of GitAnalyzer that manages repository analysis operations.
    """

    def __init__(self, 
                 repository_path: Union[str, List[str]],
                 target_commit: Optional[str] = None,
                 start_date: Optional[datetime] = None,
                 date_filter: Optional[datetime] = None,
                 end_date: Optional[datetime] = None,
                 start_commit: Optional[str] = None,
                 end_commit: Optional[str] = None,
                 start_tag: Optional[str] = None,
                 end_tag: Optional[str] = None,
                 include_references: bool = False,
                 include_remote_commits: bool = False,
                 thread_count: int = 1,
                 target_branch: Optional[str] = None,
                 file_extensions: Optional[List[str]] = None,
                 exclude_merges: bool = False,
                 author_list: Optional[List[str]] = None,
                 commit_list: Optional[List[str]] = None,
                 tagged_only: bool = False,
                 target_file: Optional[str] = None,
                 include_removed: bool = False,
                 enable_histogram: bool = False,
                 ignore_whitespace: bool = False,
                 custom_clone_path: Optional[str] = None,
                 commit_order: Optional[str] = None,
                 enable_mailmap: bool = False):
        """
        Initialize a GitRepo instance for analysis.

        Required parameter:
        - repository_path: Path to local repository or list of paths. 
          Supports both local paths and remote URLs.

        Optional parameters control various aspects of the analysis:
        - Commit selection (dates, hashes, tags)
        - Analysis behavior (threading, file types, etc.)
        - Git options (whitespace handling, mailmap usage, etc.)
        """
        
        # Convert lists to sets for better performance
        extension_set = set(file_extensions) if file_extensions else None
        commit_set = set(commit_list) if commit_list else None

        # Build configuration dictionary
        config = {
            "git_handler": None,
            "repository_path": repository_path,
            "start_commit": start_commit,
            "end_commit": end_commit,
            "start_tag": start_tag,
            "end_tag": end_tag,
            "start_date": start_date,
            "date_filter": date_filter,
            "end_date": end_date,
            "target_commit": target_commit,
            "include_references": include_references,
            "include_remote_commits": include_remote_commits,
            "thread_count": thread_count,
            "target_branch": target_branch,
            "file_extensions": extension_set,
            "exclude_merges": exclude_merges,
            "author_list": author_list,
            "commit_list": commit_set,
            "tagged_only": tagged_only,
            "ignore_whitespace": ignore_whitespace,
            "target_file": target_file,
            "include_removed": include_removed,
            "file_commits": None,
            "release_commits": None,
            "enable_histogram": enable_histogram,
            "custom_clone_path": custom_clone_path,
            "commit_order": commit_order,
            "enable_mailmap": enable_mailmap
        }
        
        self._config = Configuration(config)
        self._cleanup_required = custom_clone_path is None

    @staticmethod
    def _is_remote_repo(path: str) -> bool:
        """Check if the given path is a remote repository URL."""
        remote_prefixes = ("git@", "https://", "http://", "git://")
        return path.startswith(remote_prefixes)

    def _get_clone_directory(self) -> str:
        """Determine the directory for cloning repositories."""
        if self._config.get('custom_clone_path'):
            clone_dir = str(Path(self._config.get('custom_clone_path')))
            if not os.path.isdir(clone_dir):
                raise ValueError(f"Invalid directory path: {clone_dir}")
            return clone_dir
        
        self._tmp_dir = tempfile.TemporaryDirectory()
        return self._tmp_dir.name

    def _clone_remote_repository(self, base_dir: str, repo_url: str) -> str:
        """Clone a remote repository to the specified directory."""
        repo_name = self._extract_repo_name(repo_url)
        target_dir = os.path.join(base_dir, repo_name)
        
        if os.path.isdir(target_dir):
            logger.info(f"Using existing clone in {target_dir}")
        else:
            logger.info(f"Cloning {repo_url} to {target_dir}")
            Repo.clone_from(url=repo_url, to_path=target_dir)
        
        return target_dir

    @contextmanager
    def _prepare_repository(self, repo_path: str) -> Generator[GitHandler, None, None]:
        """Prepare repository for analysis and cleanup afterward."""
        local_path = repo_path
        if self._is_remote_repo(repo_path):
            local_path = self._clone_remote_repository(self._get_clone_directory(), repo_path)
        
        local_path = str(Path(local_path).expanduser().resolve())
        self._config.set_value('repository_path', local_path)

        git_handler = GitHandler(local_path, self._config)
        self._config.set_value("git_handler", git_handler)
        self._config.validate_filters()
        
        try:
            yield git_handler
        finally:
            self._config.set_value("git_handler", None)
            git_handler.cleanup()
            
            if self._is_remote_repo(repo_path) and self._cleanup_required:
                try:
                    self._tmp_dir.cleanup()
                except (PermissionError, OSError):
                    shutil.rmtree(self._tmp_dir.name, ignore_errors=True)

    @staticmethod
    def _extract_repo_name(url: str) -> str:
        """Extract repository name from URL."""
        last_slash = url.rfind("/")
        if last_slash < 0 or last_slash >= len(url) - 1:
            raise InvalidRepositoryURL(f"Invalid repository URL: {url}")

        end_pos = url.rfind(".git")
        if end_pos == -1:
            end_pos = len(url)

        return url[last_slash + 1:end_pos]

    def analyze_commits(self) -> Generator[Commit, None, None]:
        """
        Analyze repository commits based on configured filters.
        Returns a generator yielding Commit objects.
        """
        for repo_path in self._config.get('repository_paths'):
            with self._prepare_repository(repo_path) as git:
                logger.info(f'Analyzing repository: {git.path}')

                if self._config.get('target_file'):
                    self._config.set_value(
                        'file_commits',
                        git.get_file_commits(
                            self._config.get('target_file'),
                            self._config.get('include_removed')
                        )
                    )

                if self._config.get('tagged_only'):
                    self._config.set_value('release_commits', git.get_release_commits())

                revision, options = self._config.get_git_options()
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=self._config.get("thread_count")) as executor:
                    for result in executor.map(self._process_commit, git.get_commits(revision, **options)):
                        yield from result

    def _process_commit(self, commit: Commit) -> Generator[Commit, None, None]:
        """Process individual commits and apply filters."""
        logger.info(f'Processing commit {commit.hash} from {commit.author.name} on {commit.committer_date}')

        if not self._config.should_skip_commit(commit):
            yield commit

class InvalidRepositoryURL(Exception):
    """Raised when a repository URL is malformed."""
    pass

    def analyze_repository_commits(self) -> Generator[Commit, None, None]:
        """
        Process and analyze all commits in the repository based on configured filters.
        Yields commit objects that match the specified criteria.
        """
        for repository_path in self._config.get('repository_paths'):
            with self._setup_repository_context(repository_path) as git_handler:
                logger.info(f'Beginning analysis of repository: {git_handler.path}')

                # Handle file-specific commit analysis
                if self._config.get('target_file'):
                    self._process_file_specific_commits(git_handler)

                # Handle release tag filtering
                if self._config.get('tagged_only'):
                    self._process_tagged_commits(git_handler)

                # Get revision range and options for git
                revision_range, git_options = self._config.get_git_options()

                # Process commits using thread pool
                yield from self._process_commits_parallel(git_handler, revision_range, git_options)

    def _process_commits_parallel(self, git_handler, revision_range, options):
        """Handle parallel processing of commits using thread pool."""
        worker_count = self._config.get("thread_count")
        with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
            commit_iterator = git_handler.get_commits(revision_range, **options)
            for result in executor.map(self._analyze_single_commit, commit_iterator):
                yield from result

    def _analyze_single_commit(self, commit: Commit) -> Generator[Commit, None, None]:
        """Analyze an individual commit and determine if it should be included."""
        logger.info(f'Analyzing commit {commit.hash} by {commit.author.name} ({commit.committer_date})')
        
        if not self._config.should_skip_commit(commit):
            yield commit

    def _process_file_specific_commits(self, git_handler):
        """Process commits specific to target file."""
        self._config.set_value(
            'file_commits',
            git_handler.get_file_commits(
                self._config.get('target_file'),
                self._config.get('include_removed')
            )
        )

    def _process_tagged_commits(self, git_handler):
        """Process commits that are tagged."""
        self._config.set_value('release_commits', git_handler.get_release_commits())

    @contextmanager
    def _setup_repository_context(self, repo_path: str) -> Generator[GitHandler, None, None]:
        """Set up repository context and handle cleanup."""
        local_repo_path = self._get_repository_path(repo_path)
        
        # Configure repository path
        self._config.set_value('repository_path', local_repo_path)
        
        # Initialize git handler
        git_handler = GitHandler(local_repo_path, self._config)
        self._config.set_value("git_handler", git_handler)
        
        # Validate configuration filters
        self._config.validate_filters()
        
        try:
            yield git_handler
        finally:
            # Cleanup
            self._cleanup_repository(repo_path, git_handler)

    def _get_repository_path(self, repo_path: str) -> str:
        """Get local repository path, cloning if necessary."""
        if self._is_remote_repo(repo_path):
            clone_dir = self._get_clone_directory()
            local_path = self._clone_remote_repository(clone_dir, repo_path)
        else:
            local_path = repo_path
        
        return str(Path(local_path).expanduser().resolve())

    def _cleanup_repository(self, repo_path: str, git_handler: GitHandler):
        """Clean up repository resources."""
        self._config.set_value("git_handler", None)
        git_handler.cleanup()
        
        if self._is_remote_repo(repo_path) and self._cleanup_required:
            try:
                self._tmp_dir.cleanup()
            except (PermissionError, OSError):
                # Handle Windows cleanup issues
                shutil.rmtree(self._tmp_dir.name, ignore_errors=True)
                
    @staticmethod
    def _split_in_chunks(commits: List[Commit], worker_count: int) -> List[List[Commit]]:
        """
        Divide commits into balanced chunks for parallel processing.
        
        Args:
            commits: Complete list of commits to process
            worker_count: Number of parallel workers to distribute work across
            
        Returns:
            List of commit chunks for parallel processing
        """
        chunk_size = math.ceil(len(commits) / worker_count)
        return [
            commits[i:i + chunk_size] 
            for i in range(0, len(commits), chunk_size)
        ]

    @staticmethod
    def _extract_repo_name(url: str) -> str:
        """
        Extract repository name from a git URL.
        
        Args:
            url: Git repository URL to parse
            
        Returns:
            Repository name extracted from URL
            
        Raises:
            InvalidRepositoryURL: If URL format is invalid
        """
        # Find last path separator
        path_separator_index = url.rfind("/")
        
        # Validate URL format
        if path_separator_index < 0 or path_separator_index >= len(url) - 1:
            raise InvalidRepositoryURL(f"Invalid repository URL format: {url}")

        # Find git extension if present
        git_extension_index = url.rfind(".git")
        
        # Set end position for name extraction
        name_end_index = git_extension_index if git_extension_index != -1 else len(url)
        
        # Extract and return repo name
        return url[path_separator_index + 1:name_end_index]


class InvalidRepositoryURL(Exception):
    """Raised when a repository URL is malformed or invalid."""
    
    def __init__(self, message: str):
        super().__init__(message)