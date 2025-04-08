#!/usr/bin/env python3
"""
Main entry point for the simplified data mesh demo.
Each instance becomes a separate domain that can discover and interact with other domains.

To run multiple domains, open separate terminals and run:
python main.py <domain_name>

Examples:
Terminal 1: python main.py domain_alpha
Terminal 2: python main.py domain_beta 
Terminal 3: python main.py domain_gamma
"""

import time
import signal
import sys
import argparse
import socket
import random
from typing import List, Dict, Any

from domain import DomainController, load_domain_registry

# List to keep track of running controllers for clean shutdown
controllers = []

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

def signal_handler(sig, frame):
    """Handle Ctrl+C signal to gracefully shut down the domain."""
    print("\nShutting down domain...")
    for controller in controllers:
        controller.stop()
    sys.exit(0)

def find_available_port(start_port=9000, max_attempts=100):
    """Find an available port starting from start_port.
    
    Args:
        start_port: The port to start checking from
        max_attempts: Maximum number of ports to check
        
    Returns:
        An available port number, or None if none found
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def run_domain(domain_name):
    """Run a single domain and wait for other domains to be discovered.
    
    Args:
        domain_name: The name of the domain to run
    """
    print(f"Starting Data Mesh Domain: {domain_name}")
    print("=" * 50)
    
    # Find an available port
    port = find_available_port()
    if port is None:
        print("Error: Could not find an available port")
        sys.exit(1)
        
    # Get data for this domain
    if domain_name in DOMAIN_DATA:
        initial_data = DOMAIN_DATA[domain_name]
    else:
        # For custom domain names, use default data
        initial_data = DEFAULT_DATA.copy()
        # Add domain-specific identifier
        initial_data["domain_id"] = f"Custom data for {domain_name}"
    
    # Create and start the domain controller
    controller = DomainController(
        domain_name=domain_name,
        host="localhost",
        port=port,
        initial_data=initial_data
    )
    controllers.append(controller)
    controller.start()
    
    print(f"Domain {domain_name} started on localhost:{port}")
    print("Waiting for other domains to connect...")
    
    # Wait for controller to start
    time.sleep(1)
    
    # Main loop - periodically check for other domains
    discovery_interval = 5  # seconds
    last_discovery_time = time.time()
    other_domains = []
    
    while True:
        try:
            current_time = time.time()
            
            # Periodically check for new domains
            if current_time - last_discovery_time > discovery_interval:
                # Discover other domains
                found_domains = controller.discover_domains()
                last_discovery_time = current_time
                
                # Check for new domains
                new_domains = []
                for domain in found_domains:
                    if domain not in other_domains:
                        new_domains.append(domain)
                        other_domains.append(domain)
                
                # If new domains were found, start interaction
                if new_domains:
                    print(f"\nDiscovered {len(new_domains)} new domain(s): {', '.join(new_domains)}")
                    
                    # Start interaction with the first new domain
                    target_domain = new_domains[0]
                    host, port = controller.domain_registry[target_domain]
                    
                    print(f"Starting interaction with {target_domain}...")
                    
                    # Allow time for connection to stabilize
                    time.sleep(1)
                    
                    # Fetch data
                    print(f"Fetching data from {target_domain}...")
                    result = controller.fetch_data_from_domain(target_domain, host, port)
                    if result:
                        print(f"Successfully fetched data from {target_domain}")
                        
                        # Show combined data
                        combined_data = controller.data_product.get_combined_data()
                        print(f"Combined data:\n{combined_data}")
                        
                        # Start periodic sync
                        print(f"Starting periodic sync with {target_domain}...")
                        controller.start_periodic_sync(target_domain, interval_seconds=30)
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            signal_handler(None, None)

def run_demo():
    """Run the complete demo with a single domain and instructions."""
    print("Data Mesh Demo - No domains specified")
    print("=" * 50)
    print("\nTo run this demo properly, you need to start multiple domains in separate terminals.")
    print("\nExamples:")
    print("  Terminal 1: python main.py domain_alpha")
    print("  Terminal 2: python main.py domain_beta")
    print("  Terminal 3: python main.py custom_domain_name")
    print("\nEach terminal will become its own domain in the mesh network.")
    print("When multiple domains are running, they will automatically discover each other.")
    print("\nExiting...")
    sys.exit(0)


if __name__ == "__main__":
    # Set up signal handler for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run a Data Mesh domain")
    parser.add_argument("domain", nargs="?", help="Domain name to run")
    args = parser.parse_args()
    
    try:
        if args.domain:
            # Run a single domain
            run_domain(args.domain)
        else:
            # Show instructions
            run_demo()
    except Exception as e:
        print(f"Error running domain: {e}")
        # Clean up
        for controller in controllers:
            controller.stop()
        sys.exit(1)