#!/usr/bin/env python3
"""
Platform server for the data mesh.
This is run by the platform team to provide central services to domains.
"""

import time
import signal
import sys
import socket
from typing import List
import argparse

from platform.registry import get_registry
from platform.discovery import get_discovery_service
from platform.connectivity import MessagingService
import config

# Global service references for clean shutdown
registry = None
discovery_service = None
messaging_service = None

def signal_handler(sig, frame):
    """Handle Ctrl+C signal to gracefully shut down the platform."""
    print("\nShutting down platform...")
    
    if messaging_service:
        messaging_service.stop()
        
    if discovery_service:
        discovery_service.stop()
        
    sys.exit(0)

def parse_arguments():
    """Parse command line arguments.
    
    Returns:
        The parsed arguments
    """
    parser = argparse.ArgumentParser(description="Data Mesh Platform Server")
    
    parser.add_argument(
        "--host", 
        default=config.get_default_host(),
        help=f"Host to bind the server to (default: {config.get_default_host()})"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=config.PLATFORM_PORT,
        help=f"Port to bind the server to (default: {config.PLATFORM_PORT})"
    )
    
    return parser.parse_args()

def run_platform_server(host, port):
    """Run the platform server.
    
    Args:
        host: The host to bind the server to
        port: The port to bind the server to
    """
    global registry, discovery_service, messaging_service
    
    print(f"Starting Data Mesh Platform on {host}:{port}")
    print("=" * 50)
    
    # Get the registry service
    registry = get_registry()
    print("Registry service initialized")
    
    # Start the discovery service
    discovery_service = get_discovery_service()
    discovery_service.start()
    print("Discovery service started")
    
    # Start the messaging service
    messaging_service = MessagingService(host, port)
    messaging_service.start()
    print("Messaging service started")
    
    print(f"\nPlatform is running on {host}:{port}")
    print("Press Ctrl+C to stop")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    # Set up signal handler for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse command line arguments
    args = parse_arguments()
    
    try:
        # Run the platform server
        run_platform_server(args.host, args.port)
    except Exception as e:
        print(f"Error running platform server: {e}")
        sys.exit(1)