#!/usr/bin/env python3
"""
Main entry point for the data mesh demo.
Starts up the domain controllers and demonstrates communication between them.
"""

import time
import signal
import sys
from typing import List

from infra.discovery import REGISTRY, list_domains
from domain_alpha.controller import AlphaController
from domain_beta.controller import BetaController

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
    print("Starting Data Mesh Socket Demo")
    print("=" * 50)

    # Print available domains
    print("Available domains:")
    domains = list_domains()
    for domain, address in domains.items():
        host, port = address
        print(f"  - {domain}: {host}:{port}")
    print("=" * 50)

    # Start Alpha domain
    alpha_host, alpha_port = REGISTRY["domain_alpha"]
    alpha_controller = AlphaController(alpha_host, alpha_port)
    alpha_controller.start()
    controllers.append(alpha_controller)

    # Give Alpha a moment to start up
    time.sleep(1)

    # Start Beta domain
    beta_host, beta_port = REGISTRY["domain_beta"]
    beta_controller = BetaController(beta_host, beta_port)
    beta_controller.start()
    controllers.append(beta_controller)

    # Give Beta a moment to start up
    time.sleep(1)

    # Demonstrate communication
    print("\nDemonstrating domain communication:")
    print("-" * 50)

    # Beta fetches data from Alpha
    print("\n1. Beta fetches data from Alpha:")
    result = beta_controller.fetch_data_from_alpha()
    print(f"Fetch successful: {result}")

    # Get combined data from Beta
    print("\n2. Getting combined data from Beta:")
    time.sleep(1)  # Brief pause for clarity in output
    combined_data = beta_controller.data_product.get_combined_data()
    print(f"Combined data: {combined_data}")

    # Start periodic sync
    print("\n3. Starting periodic sync from Beta to Alpha (every 10 seconds):")
    beta_controller.start_periodic_sync(interval_seconds=10)

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