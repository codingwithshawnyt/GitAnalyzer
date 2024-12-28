
"""
GitAnalyzer's core Git repository interface module.
This module contains the GitRepo class for Git repository analysis.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Optional, Set, Generator

from git import Repo, GitCommandError
from git.objects import Commit as GitPythonCommit

from gitanalyzer.domain.commit import Commit, ChangeType, ChangedFile
from gitanalyzer.utils.config import Configuration

# Configure logging
log = logging.getLogger(__name__)


class GitRepo:
    """
    Core class for Git repository analysis in GitAnalyzer.
    Provides functionality for commit analysis, checkout operations, and repository management.
    """

    def __init__(self, repository_path: str, config: Optional[Configuration] = None):
        """
        Initialize a new Git repository interface.

        Args:
            repository_path (str): Path to the Git repository
            config (Configuration, optional): Custom configuration settings
        """
        self.repo_path = Path(repository_path).expanduser().resolve()
        self.repo_name = self.repo_path.name
        self.git_repo = None

        # Create default configuration if none provided
        self.config = config or Configuration({
            "repository_path": str(self.repo_path),
            "repository": self
        })

        # Initialize with no main branch
        self.config.update("primary_branch", None)
        
        # Set up repository connection
        self._initialize_repository()

    @property
    def repository(self) -> Repo:
        """
        Access the underlying GitPython repository object.

        Returns:
            Repo: The GitPython repository instance
        """
        if not self.git_repo:
            self._initialize_repository()

        assert self.git_repo, "Repository not properly initialized"
        return self.git_repo

    def cleanup(self):
        """
        Clean up repository resources.
        Important for Windows systems where GitPython may leak resources.
        """
        if self.git_repo:
            self.repository.git.clear_cache()

    def _initialize_repository(self):
        """Set up the Git repository connection and configure basic settings."""
        self.git_repo = Repo(str(self.repo_path))
        
        # Configure Git to mark unblameable lines
        self.git_repo.config_writer().set_value(
            "blame", "markUnblamableLines", "true"
        ).release()

        # Detect primary branch if not set
        if self.config.get("primary_branch") is None:
            self._detect_primary_branch()

    def _detect_primary_branch(self):
        """Identify and store the repository's primary branch name."""
        try:
            primary = self.git_repo.active_branch.name
            self.config.update("primary_branch", primary)
        except TypeError:
            log.info("Repository HEAD is detached, setting primary branch to empty string")
            self.config.update("primary_branch", '')

    def get_current_commit(self) -> Commit:
        """
        Retrieve the current HEAD commit.

        Returns:
            Commit: The current HEAD commit
        """
        return Commit(self.repository.head.commit, self.config)

    def get_commits(self, revision='HEAD', **kwargs) -> Generator[Commit, None, None]:
        """
        Generate a sequence of repository commits.

        Args:
            revision (str): Starting revision/commit (defaults to HEAD)
            **kwargs: Additional arguments for commit iteration

        Yields:
            Generator[Commit]: A sequence of commit objects

        Raises:
            Exception: If there's an error accessing commits
        """
        # Default to reverse chronological order
        kwargs.setdefault('reverse', True)

        try:
            for git_commit in self.repository.iter_commits(rev=revision, **kwargs):
                yield self._convert_git_commit(git_commit)
        except GitCommandError as error:
            if "fatal: bad revision 'HEAD'" in str(error):
                log.debug(f"No commits found in {self.repo_path}")
            else:
                raise Exception(f"Failed to retrieve commits: {error}")

    def _convert_git_commit(self, git_commit: GitPythonCommit) -> Commit:
        """
        Convert a GitPython commit to a GitAnalyzer commit object.

        Args:
            git_commit (GitPythonCommit): GitPython commit object

        Returns:
            Commit: GitAnalyzer commit object
        """
        return Commit(git_commit, self.config)
    
    def get_commit_by_hash(self, commit_hash: str) -> Commit:
        """
        Retrieve a specific commit by its hash.

        Args:
            commit_hash (str): Hash identifier of the commit

        Returns:
            Commit: The requested commit object
        """
        git_commit = self.repository.commit(commit_hash)
        return self._convert_git_commit(git_commit)

    def convert_gitpython_commit(self, git_commit: GitPythonCommit) -> Commit:
        """
        Convert a native GitPython commit object to a GitAnalyzer commit.
        This is an internal method primarily used for system integration.

        Args:
            git_commit (GitPythonCommit): Native GitPython commit object

        Returns:
            Commit: Converted GitAnalyzer commit object
        """
        return self._convert_git_commit(git_commit)

    def switch_to_commit(self, commit_hash: str) -> None:
        """
        Switch the repository state to a specific commit.
        
        Warning:
            This operation modifies the repository state and is not thread-safe.
            Use with caution in multi-threaded environments.

        Args:
            commit_hash (str): Hash of the target commit
        """
        self.repository.git.checkout('-f', commit_hash)

    def list_repository_files(self) -> List[str]:
        """
        Get all files in the repository, excluding the .git directory.

        Returns:
            List[str]: Full paths of all files in the repository
        """
        file_list = []
        for root, _, filenames in os.walk(str(self.repo_path)):
            if '.git' in root:
                continue
            for filename in filenames:
                file_list.append(os.path.join(root, filename))
        return file_list

    def reset_to_main(self) -> None:
        """
        Reset the repository to the main branch, discarding all local changes.
        Uses force checkout to ensure clean state.
        """
        self.repository.git.checkout('-f', self.config.get("primary_branch"))

    def count_total_commits(self) -> int:
        """
        Get the total number of commits in the repository.

        Returns:
            int: Total number of commits
        """
        return len(list(self.get_commits()))

    def get_commit_by_tag(self, tag_name: str) -> Commit:
        """
        Retrieve a commit referenced by a specific tag.

        Args:
            tag_name (str): Name of the tag

        Returns:
            Commit: The commit referenced by the tag

        Raises:
            IndexError, AttributeError: If tag doesn't exist or is invalid
        """
        try:
            tag = self.repository.tags[tag_name]
            return self.get_commit_by_hash(tag.commit.hexsha)
        except (IndexError, AttributeError):
            log.debug(f"Failed to find tag: {tag_name}")
            raise

    def get_all_tagged_commits(self) -> List[str]:
        """
        Get commit hashes for all tagged commits in the repository.

        Returns:
            List[str]: List of commit hashes that have tags
        """
        return [tag.commit.hexsha 
                for tag in self.repository.tags 
                if tag.commit]

    def analyze_commit_changes(self, 
                             commit: Commit,
                             specific_file: Optional[ChangedFile] = None,
                             ignore_commits_file: Optional[str] = None) -> Dict[str, Set[str]]:
        """
        Analyze which commits last modified the lines changed in a given commit.
        Implements SZZ algorithm to track line modifications.

        Process:
        1. Extract file differences
        2. Identify removed lines
        3. Use git blame to find commits that introduced the modified lines

        Args:
            commit (Commit): Target commit to analyze
            specific_file (ChangedFile, optional): Limit analysis to specific file
            ignore_commits_file (str, optional): Path to file listing commits to ignore

        Returns:
            Dict[str, Set[str]]: Mapping of files to sets of commit hashes
        """
        modifications = [specific_file] if specific_file else commit.modified_files
        return self._calculate_last_commits(commit, modifications, ignore_commits_file)
    
    def compare_commits(self, start_commit: str, end_commit: str) -> List[ChangedFile]:
        """
        Compare two commits and get the list of modified files between them.

        Args:
            start_commit (str): Hash of the starting commit
            end_commit (str): Hash of the ending commit

        Returns:
            List[ChangedFile]: List of files modified between the commits
        """
        start = self.repository.commit(start_commit)
        end = self.repository.commit(end_commit)
        diff_index = start.diff(
            other=end,
            paths=None,
            create_patch=True
        )

        return [ChangedFile(diff=diff) for diff in diff_index]

    def _analyze_commit_history(self, commit: Commit,
                              changes: List[ChangedFile],
                              ignore_hashes_file: Optional[str] = None) -> Dict[str, Set[str]]:
        """
        Analyze the commit history to find the origin of changed lines.

        Args:
            commit (Commit): The commit to analyze
            changes (List[ChangedFile]): List of file changes to analyze
            ignore_hashes_file (Optional[str]): Path to file containing commit hashes to ignore

        Returns:
            Dict[str, Set[str]]: Mapping of file paths to sets of related commit hashes
        """
        commit_history: Dict[str, Set[str]] = {}

        for change in changes:
            file_path = change.new_path
            if change.change_type in [ChangeType.RENAME, ChangeType.DELETE]:
                file_path = change.old_path

            removed_lines = change.diff_parsed['deleted']
            
            if file_path is None:
                raise ValueError("File path could not be determined")

            try:
                blame_info = self._get_file_blame(commit.hash, file_path, ignore_hashes_file)
                
                for line_num, content in removed_lines:
                    if self._is_significant_line(content.strip()):
                        origin_commit = blame_info[line_num - 1].split(' ')[0].replace('^', '')

                        # Skip lines marked as unblameable
                        if origin_commit.startswith("*"):
                            continue

                        # Update path for renamed files
                        if change.change_type == ChangeType.RENAME:
                            file_path = change.new_path

                        if file_path is None:
                            raise ValueError("File path could not be determined")
                            
                        commit_history.setdefault(file_path, set()).add(
                            self.get_commit_by_hash(origin_commit).hash
                        )
            except GitCommandError:
                log.debug(f"File {change.filename} not found in commit {commit.hash}. Possible double rename.")

        return commit_history

    def _get_file_blame(self, commit_hash: str, file_path: str, 
                       ignore_hashes_file: Optional[str] = None) -> List[str]:
        """
        Get git blame information for a file at a specific commit.

        Args:
            commit_hash (str): Hash of the commit
            file_path (str): Path to the file
            ignore_hashes_file (Optional[str]): Path to file containing hashes to ignore

        Returns:
            List[str]: Lines of git blame output
        """
        blame_args = ['-w', f'{commit_hash}^']
        
        if ignore_hashes_file:
            if self.repository.git.version_info >= (2, 23):
                blame_args.extend(["--ignore-revs-file", ignore_hashes_file])
            else:
                log.info("Git version < 2.23 does not support --ignore-revs-file")
                
        return self.repository.git.blame(*blame_args, '--', file_path).split('\n')

    @staticmethod
    def _is_significant_line(line: str) -> bool:
        """
        Determine if a line contains significant code (not comments or whitespace).

        Args:
            line (str): The line to check

        Returns:
            bool: True if the line contains significant code, False otherwise
        """
        comment_markers = [
            '', '//', '#', '/*', "'''", '"""', '*'
        ]
        return not any(line.startswith(marker) for marker in comment_markers)

    def get_file_commit_history(self, file_path: str, include_deletions: bool = False) -> List[str]:
        """
        Get the complete commit history for a specific file.

        Args:
            file_path (str): Path to the file
            include_deletions (bool): Whether to include commits where the file was deleted

        Returns:
            List[str]: List of commit hashes that modified the file
        """
        path = str(Path(file_path))
        commit_hashes = []

        try:
            log_command = ["--follow", "--format=%H"]
            if include_deletions:
                log_command.extend(["--", path])
            else:
                log_command.append(path)
                
            commit_hashes = self.repository.git.log(*log_command).split('\n')
        except GitCommandError:
            log.debug(f"Could not retrieve history for file: {path}")

        return commit_hashes

    def __del__(self):
        """Cleanup repository resources when the object is destroyed."""
        self.cleanup()