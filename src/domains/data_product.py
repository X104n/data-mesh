"""
Data Product module for domain teams.
Provides base class for creating domain-specific data products.
"""

from typing import Dict, Any, Optional, List
import json

class DataProduct:
    """Base class for domain data products."""
    
    def __init__(self, domain_name: str, data: Dict[str, Any] = None):
        """Initialize a data product.
        
        Args:
            domain_name: The name of the domain this data product belongs to
            data: Initial data dictionary (optional)
        """
        self.domain_name = domain_name
        self.product_name = f"{domain_name.capitalize()}DataProduct"
        self.version = "1.0"
        
        # Initialize with provided data or empty dict
        self._data = data or {}
        
        # Storage for data from other domains
        self._external_data = {}
    
    def get_data(self) -> Dict[str, Any]:
        """Get all data from this domain.
        
        Returns:
            The domain's data as a dictionary
        """
        return {
            "domain": self.domain_name,
            "product": self.product_name,
            "version": self.version,
            "data": self._data
        }
    
    def get_data_as_string(self) -> str:
        """Get a string representation of the domain's data.
        
        Returns:
            A string representation of the domain's data
        """
        return f"Hello from {self.product_name}! Here's the data: {list(self._data.values())}"
    
    def get_item(self, item_id: str) -> Optional[Any]:
        """Get a specific item by ID.
        
        Args:
            item_id: The ID of the item to retrieve
            
        Returns:
            The requested item or None if not found
        """
        return self._data.get(item_id)
    
    def store_item(self, item_id: str, value: Any) -> None:
        """Store a specific item.
        
        Args:
            item_id: The ID of the item to store
            value: The value to store
        """
        self._data[item_id] = value
        print(f"[{self.domain_name}] Stored item {item_id}")
    
    def store_external_data(self, source_domain: str, data: Any) -> None:
        """Store data received from another domain.
        
        Args:
            source_domain: The name of the domain that provided the data
            data: The data received
        """
        self._external_data[source_domain] = data
        print(f"[{self.domain_name}] Stored data from {source_domain}")
    
    def get_combined_data(self) -> Dict[str, Any]:
        """Get a combination of this domain's data and data from other domains.
        
        Returns:
            A dictionary containing all available data
        """
        result = {
            "domain_data": self._data,
            "external_data": self._external_data
        }
        
        return result
    
    def get_combined_data_as_string(self) -> str:
        """Get a string representation of combined data.
        
        Returns:
            A string representation of all available data
        """
        result = [f"Data from {self.domain_name}: {list(self._data.values())}"]
        
        for domain, data in self._external_data.items():
            result.append(f"Data from {domain}: {data}")
            
        return "\n".join(result)