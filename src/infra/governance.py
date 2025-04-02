"""
Discovery module for the data mesh demo.
Maintains a registry of available domains and their connection details.
"""

from typing import Dict, Tuple, Optional

# Simple registry mapping domain names to (host, port) tuples
REGISTRY: Dict[str, Tuple[str, int]] = {
    "domain_alpha": ("localhost", 9001),
    "domain_beta": ("localhost", 9002)
}

# Minimal metadata about each domain
DOMAIN_METADATA: Dict[str, Dict[str, str]] = {
    "domain_alpha": {
        "version": "1.0",
        "description": "Alpha domain providing sample data",
        "owner": "Alpha Team"
    },
    "domain_beta": {
        "version": "1.0",
        "description": "Beta domain consuming data from Alpha",
        "owner": "Beta Team"
    }
}


def get_domain_address(domain_name: str) -> Optional[Tuple[str, int]]:
    """Get the (host, port) tuple for a domain.

    Args:
        domain_name: The name of the domain to look up

    Returns:
        A tuple of (host, port) if the domain exists, None otherwise
    """
    return REGISTRY.get(domain_name)


def get_domain_metadata(domain_name: str) -> Optional[Dict[str, str]]:
    """Get metadata for a domain.

    Args:
        domain_name: The name of the domain to look up

    Returns:
        A dictionary of metadata if the domain exists, None otherwise
    """
    return DOMAIN_METADATA.get(domain_name)


def list_domains() -> Dict[str, Tuple[str, int]]:
    """List all available domains.

    Returns:
        A dictionary mapping domain names to (host, port) tuples
    """
    return REGISTRY.copy()