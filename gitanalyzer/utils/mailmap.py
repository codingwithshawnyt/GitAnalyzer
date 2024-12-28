import subprocess
from abc import ABC, abstractmethod
from typing import Optional, Tuple


class Author:
    """Represents a code author with name and email."""
    def __init__(self, name: Optional[str] = None, email: Optional[str] = None):
        self.name = name
        self.email = email

    def __eq__(self, other):
        if not isinstance(other, Author):
            return False
        return self.name == other.name and self.email == other.email

    def __hash__(self):
        return hash((self.name, self.email))


class AuthorFactoryBase(ABC):
    """Base class for creating Author instances."""
    @abstractmethod
    def create_author(self, name: Optional[str] = None, email: Optional[str] = None) -> Author:
        """Abstract method to create an Author instance."""
        pass


class SimpleAuthorFactory(AuthorFactoryBase):
    """Creates Author instances without any mapping."""
    def create_author(self, name: Optional[str] = None, email: Optional[str] = None) -> Author:
        return Author(name, email)


class GitMailMapAuthorFactory(AuthorFactoryBase):
    """Creates Author instances with mailmap support for canonical names/emails."""
    
    def __init__(self, config):
        self.mailmap_lookup_cache = {}
        self.repo_path = config.get('path_to_repo')

    def _get_canonical_identity(self, name: Optional[str] = None, 
                              email: Optional[str] = None) -> Tuple[str, str]:
        """
        Queries git check-mailmap to get canonical identity information.
        
        Uses the repository's .mailmap file to resolve the canonical name and email
        for a given author. Documentation available at:
        https://github.com/codingwithshawnyt/GitAnalyzer
        
        Args:
            name: Author's display name
            email: Author's email address
            
        Returns:
            Tuple containing canonical (name, email)
        """
        try:
            git_process = subprocess.run(
                ["git", "-C", self.repo_path, "check-mailmap", f"{name} <{email}>"],
                capture_output=True,
                text=True
            )

            if git_process.stdout:
                output = git_process.stdout.strip()
                
                # Handle email-only case
                if output.startswith("<"):
                    return "", output[1:-1]
                
                # Handle normal name + email case
                parts = output.split(" <")
                canonical_name = parts[0]
                canonical_email = parts[1][:-1]
                return canonical_name, canonical_email
                
            # Return original values if git command produced no output
            return str(name), str(email)
            
        except Exception:
            # Fallback to original values on any error
            return str(name), str(email)

    def create_author(self, name: Optional[str] = None, email: Optional[str] = None) -> Author:
        """
        Creates an Author instance with canonical identity information.
        
        Checks the cache first for previously mapped authors. If not found,
        queries git check-mailmap and caches the result for future lookups.
        
        Args:
            name: Author's display name
            email: Author's email address
            
        Returns:
            Author instance with canonical identity information
        """
        original_author = Author(name, email)
        
        # Return cached mapping if available
        if cached_author := self.mailmap_lookup_cache.get(original_author):
            return cached_author

        try:
            # Get and cache new mapping
            canonical_name, canonical_email = self._get_canonical_identity(name, email)
            mapped_author = Author(canonical_name, canonical_email)
            self.mailmap_lookup_cache[original_author] = mapped_author
            return mapped_author
            
        except Exception:
            # Fallback to original author on any error
            return original_author
