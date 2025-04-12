"""
Registry module for the data mesh platform.
Provides a centralized registry service for domains to register and discover each other.
"""

import os
import pickle
import time
import threading
from typing import Dict, Any, List, Optional

# Define the registry file path - will be in the user's home directory
REGISTRY_FILE = os.path.join(os.path.expanduser("~"), ".data_mesh_registry")

class DomainRegistry:
    """Centralized registry service for the data mesh platform."""
    
    def __init__(self):
        """Initialize the domain registry."""
        self._registry = self._load_registry()
        self._lock = threading.Lock()
        
        # Start automatic cleanup of stale entries
        self._cleanup_thread = threading.Thread(target=self._cleanup_job)
        self._cleanup_thread.daemon = True
        self._cleanup_thread.start()
    
    def register_domain(self, domain_name: str, host: str, port: int) -> bool:
        """Register a domain in the central registry.
        
        Args:
            domain_name: The name of the domain to register
            host: The host where the domain is running
            port: The port the domain is listening on
            
        Returns:
            True if registration was successful, False otherwise
        """
        with self._lock:
            self._registry[domain_name] = {
                "host": host,
                "port": port,
                "timestamp": time.time()
            }
            self._save_registry()
            print(f"[Registry] Registered domain {domain_name} at {host}:{port}")
            return True
    
    def unregister_domain(self, domain_name: str) -> bool:
        """Unregister a domain from the central registry.
        
        Args:
            domain_name: The name of the domain to unregister
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        with self._lock:
            if domain_name in self._registry:
                del self._registry[domain_name]
                self._save_registry()
                print(f"[Registry] Unregistered domain {domain_name}")
                return True
            return False
    
    def get_domains(self, exclude_domain: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Get all registered domains.
        
        Args:
            exclude_domain: Optional domain name to exclude from the results
            
        Returns:
            Dictionary of domain information
        """
        with self._lock:
            # Create a copy of the registry to avoid modification during iteration
            registry_copy = self._registry.copy()
            
            # Exclude the specified domain if requested
            if exclude_domain and exclude_domain in registry_copy:
                registry_copy.pop(exclude_domain)
                
            return registry_copy
    
    def get_domain(self, domain_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific domain.
        
        Args:
            domain_name: The name of the domain to retrieve
            
        Returns:
            Domain information or None if not found
        """
        with self._lock:
            return self._registry.get(domain_name)
    
    def _cleanup_job(self) -> None:
        """Background job to clean up stale domain entries."""
        while True:
            time.sleep(300)  # Run every 5 minutes
            self._cleanup_stale_entries()
    
    def _cleanup_stale_entries(self) -> None:
        """Remove stale entries from the registry."""
        with self._lock:
            current_time = time.time()
            stale_domains = []
            
            # Find domains that haven't updated in the last hour
            for domain_name, info in self._registry.items():
                if current_time - info.get("timestamp", 0) > 3600:  # 1 hour
                    stale_domains.append(domain_name)
            
            # Remove stale domains
            for domain_name in stale_domains:
                del self._registry[domain_name]
                print(f"[Registry] Removed stale domain {domain_name}")
            
            # Save if we removed any domains
            if stale_domains:
                self._save_registry()
    
    def _save_registry(self) -> None:
        """Save the registry to a file."""
        try:
            with open(REGISTRY_FILE, 'wb') as f:
                pickle.dump(self._registry, f)
        except Exception as e:
            print(f"[Registry] Error saving registry: {e}")

    def _load_registry(self) -> Dict[str, Dict[str, Any]]:
        """Load the registry from a file.
        
        Returns:
            The loaded registry or an empty dict if the file doesn't exist
        """
        try:
            if os.path.exists(REGISTRY_FILE):
                with open(REGISTRY_FILE, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            print(f"[Registry] Error loading registry: {e}")
        return {}

# Singleton instance
_registry_instance = None

def get_registry() -> DomainRegistry:
    """Get the singleton instance of the domain registry.
    
    Returns:
        The domain registry instance
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = DomainRegistry()
    return _registry_instance