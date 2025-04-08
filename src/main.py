#!/usr/bin/env python3
"""
Main entry point for the simplified data mesh demo.
Starts up domain controllers and demonstrates communication between them.
"""

import time
import signal
import sys
from typing import List

from domain import DomainController

# List to keep track of running controllers for clean shutdown
controllers = []


def signal_handler(sig, frame):
    """Handle Ctrl+C signal to gracefully shut down the demo."""
    print("\nShutting down data mesh demo...")
    for controller in controllers:
        controller.stop()
    sys.exit(0)


def run_demo():
    """Run the data mesh demo."""
    print("Starting Simplified Data Mesh Demo")
    print("=" * 50)

    # Domain configuration - could be loaded from a config file
    domains = {
        "domain_alpha": {
            "host": "localhost",
            "port": 9001,
            "data": {
                "item1": "Alpha data point 1",
                "item2": "Alpha data point 2",
                "item3": "Alpha data point 3",
            }
        },
        "domain_beta": {
            "host": "localhost",
            "port": 9002,
            "data": {
                "analysis1": "Beta analysis of Alpha data",
                "analysis2": "Another Beta analysis",
            }
        }
    }

    # Print available domains
    print("Available domains:")
    for domain_name, config in domains.items():
        host, port = config["host"], config["port"]
        print(f"  - {domain_name}: {host}:{port}")
    print("=" * 50)

    # Start all domains
    domain_controllers = {}
    
    for domain_name, config in domains.items():
        controller = DomainController(
            domain_name=domain_name,
            host=config["host"],
            port=config["port"],
            initial_data=config.get("data", {})
        )
        controller.start()
        controllers.append(controller)
        domain_controllers[domain_name] = controller
        
        # Give controller a moment to start up
        time.sleep(0.5)
        
        # Register other domains in this controller
        for other_domain, other_config in domains.items():
            if other_domain != domain_name:
                controller.register_domain(
                    other_domain,
                    other_config["host"],
                    other_config["port"]
                )

    # Demonstrate communication
    print("\nDemonstrating domain communication:")
    print("-" * 50)

    # Beta fetches data from Alpha
    alpha_host = domains["domain_alpha"]["host"]
    alpha_port = domains["domain_alpha"]["port"]
    
    print("\n1. Beta fetches data from Alpha:")
    result = domain_controllers["domain_beta"].fetch_data_from_domain(
        "domain_alpha", alpha_host, alpha_port
    )
    print(f"Fetch successful: {result}")

    # Get combined data from Beta
    print("\n2. Getting combined data from Beta:")
    time.sleep(1)  # Brief pause for clarity in output
    combined_data = domain_controllers["domain_beta"].data_product.get_combined_data()
    print(f"Combined data: {combined_data}")

    # Start periodic sync
    print("\n3. Starting periodic sync from Beta to Alpha (every 10 seconds):")
    domain_controllers["domain_beta"].start_periodic_sync("domain_alpha", interval_seconds=10)

    # Keep the demo running
    print("\nData mesh demo is running. Press Ctrl+C to stop.")
    print("=" * 50)
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            signal_handler(None, None)


if __name__ == "__main__":
    # Set up signal handler for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)

    try:
        run_demo()
    except Exception as e:
        print(f"Error running demo: {e}")
        # Clean up
        for controller in controllers:
            controller.stop()
        sys.exit(1)