"""
Module containing the Developer entity for representing Git contributors.
Repository: https://github.com/codingwithshawnyt/GitAnalyzer
"""

from typing import Optional, Any


class Developer:
    """
    Represents a Git contributor with their identifying information.
    Stores basic details like name and contact information.
    """
    
    def __init__(self, full_name: Optional[str] = None, contact_email: Optional[str] = None) -> None:
        """
        Initialize a new Developer instance.
        
        Args:
            full_name: The developer's full name (optional)
            contact_email: The developer's email address (optional)
        """
        self.name = full_name
        self.email = contact_email

    def __eq__(self, other: Any) -> bool:
        """
        Compare this developer with another object for equality.
        
        Args:
            other: Object to compare with
            
        Returns:
            bool: True if both objects are equal, False otherwise
        """
        if not isinstance(other, self.__class__):
            return NotImplemented
        
        if other is self:
            return True
            
        return (self.name == other.name and 
                self.email == other.email)

    def __hash__(self) -> int:
        """
        Generate a hash value for the Developer instance.
        
        Returns:
            int: Hash value based on the string representation
        """
        return hash(self.to_string())

    def to_string(self) -> str:
        """
        Create a string representation of the developer.
        
        Returns:
            str: Formatted string with name and email
        """
        return f"{self.name}, <{self.email}>"

    def __str__(self) -> str:
        """
        String representation for informal display.
        
        Returns:
            str: Human-readable string representation
        """
        return self.to_string()

    def __repr__(self) -> str:
        """
        String representation for debugging and development.
        
        Returns:
            str: Detailed string representation for reproduction
        """
        return f'{self.__class__.__name__}(full_name="{self.name}", contact_email="{self.email}")'
