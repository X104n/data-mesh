"""
Configuration module for the data mesh.
Contains shared configuration and constants.
"""

import socket
import os

# Platform server configuration
PLATFORM_HOST = "10.0.3.6"
PLATFORM_PORT = 9000

# Available IP addresses for computers in the network
AVAILABLE_IPS = ["10.0.3.4", "10.0.3.5", "10.0.3.6", "10.0.3.7"]

# Default port range for domains
DOMAIN_PORT_START = 9000
DOMAIN_PORT_RANGE = 100

# Registry file location
REGISTRY_FILE = os.path.join(os.path.expanduser("~"), ".data_mesh_registry")

# Sample data for different domains
DOMAIN_DATA = {
    "domain_alpha": {
        "item1": "Alpha data point 1",
        "item2": "Alpha data point 2",
        "item3": "Alpha data point 3",
    },
    "domain_beta": {
        "analysis1": "Beta analysis of Alpha data",
        "analysis2": "Another Beta analysis",
    },
    "domain_gamma": {
        "metric1": "Gamma metric 1",
        "metric2": "Gamma metric 2",
    }
}

# Default data for any custom domain name
DEFAULT_DATA = {
    "data1": "Custom domain data 1",
    "data2": "Custom domain data 2",
}

def find_available_port(start_port=DOMAIN_PORT_START, max_attempts=DOMAIN_PORT_RANGE):
    """Find an available port starting from start_port.
    
    Args:
        start_port: The port to start searching from
        max_attempts: The maximum number of ports to try
        
    Returns:
        An available port or None if no port is available
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    return None

def get_default_host():
    """Get a default host for this machine.
    
    Returns:
        A hostname or IP address
    """
    # Try to get the local hostname
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "localhost"