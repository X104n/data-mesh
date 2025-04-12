#!/usr/bin/env python3
"""
Domain application for the data mesh.
Each instance becomes a separate domain that can discover and interact with other domains.
"""

import time
import signal
import sys
import socket
import argparse
from typing import List, Dict, Any

from domains.domain_client import DomainClient
import config

# List to keep track of running domains for clean shutdown
domains = []

def signal_handler(sig, frame):
    """Handle Ctrl+C signal to gracefully shut down the domain."""
    print("\nShutting down domain...")
    for domain in domains:
        domain.stop()
    sys.exit(0)

def get_ip_choice():
    """Prompt the user to choose their local IP address."""
    print("\nSelect your computer's IP address:")
    for i, ip in enumerate(config.AVAILABLE_IPS, 1):
        print(f"{i}. {ip}")
    
    # Get user choice
    while True:
        try:
            choice = input("\nEnter your choice (number): ")
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(config.AVAILABLE_IPS):
                return config.AVAILABLE_IPS[choice_num - 1]
            else:
                print(f"Please enter a number between 1 and {len(config.AVAILABLE_IPS)}")
        except ValueError:
            print("Please enter a valid number")

def get_domain_choice():
    """Prompt the user to choose or enter a domain name."""
    print("Data Mesh Domain Selection")
    print("=" * 50)
    
    # List available predefined domains
    print("\nAvailable domains:")
    for i, domain in enumerate(config.DOMAIN_DATA.keys(), 1):
        print(f"{i}. {domain}")
    print(f"{len(config.DOMAIN_DATA) + 1}. Custom domain (enter your own name)")
    
    # Get user choice
    while True:
        try:
            choice = input("\nEnter your choice (number): ")
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(config.DOMAIN_DATA):
                # User selected a predefined domain
                return list(config.DOMAIN_DATA.keys())[choice_num - 1]
            elif choice_num == len(config.DOMAIN_DATA) + 1:
                # User wants to enter a custom domain
                custom_name = input("Enter custom domain name: ").strip()
                if custom_name and " " not in custom_name:
                    return custom_name
                else:
                    print("Invalid domain name. Please use a single word without spaces.")
            else:
                print(f"Please enter a number between 1 and {len(config.DOMAIN_DATA) + 1}")
        except ValueError:
            print("Please enter a valid number")

def parse_arguments():
    """Parse command line arguments.
    
    Returns:
        The parsed arguments
    """
    parser = argparse.ArgumentParser(description="Data Mesh Domain Application")
    
    parser.add_argument(
        "--domain", 
        help="Domain name (if not provided, will prompt)"
    )
    
    parser.add_argument(
        "--host", 
        help="Host to bind the domain to (if not provided, will prompt)"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        help="Port to bind the domain to (if not provided, will use available port)"
    )
    
    parser.add_argument(
        "--platform-host", 
        default=config.PLATFORM_HOST,
        help=f"Platform host (default: {config.PLATFORM_HOST})"
    )
    
    parser.add_argument(
        "--platform-port", 
        type=int, 
        default=config.PLATFORM_PORT,
        help=f"Platform port (default: {config.PLATFORM_PORT})"
    )
    
    parser.add_argument(
        "--interactive", 
        action="store_true",
        help="Run in interactive mode"
    )
    
    return parser.parse_args()

def run_domain(domain_name, local_ip, port, platform_host, platform_port, interactive=False):
    """Run a single domain and connect to the platform.
    
    Args:
        domain_name: Name of the domain to run
        local_ip: IP address of this computer
        port: Port for the domain to listen on
        platform_host: Host of the platform server
        platform_port: Port of the platform server
        interactive: Whether to run in interactive mode
    """
    print(f"\nStarting Data Mesh Domain: {domain_name} on {local_ip}:{port}")
    print("=" * 50)
    
    # Get data for this domain
    if domain_name in config.DOMAIN_DATA:
        initial_data = config.DOMAIN_DATA[domain_name]
    else:
        # For custom domain names, use default data
        initial_data = config.DEFAULT_DATA.copy()
        # Add domain-specific identifier
        initial_data["domain_id"] = f"Custom data for {domain_name}"
    
    # Create and start the domain client
    domain = DomainClient(
        domain_name=domain_name,
        host=local_ip,
        port=port,
        platform_host=platform_host,
        platform_port=platform_port,
        initial_data=initial_data
    )
    domains.append(domain)
    
    success = domain.start()
    if not success:
        print(f"Failed to start domain {domain_name}")
        return
    
    print(f"Domain {domain_name} started on {local_ip}:{port}")
    print(f"Connected to platform at {platform_host}:{platform_port}")
    
    # Wait for a moment to let registration complete
    time.sleep(1)
    
    # In interactive mode, allow the user to control the domain
    if interactive:
        run_interactive_mode(domain)
    else:
        # Just run in background mode
        print("Running in background mode. Press Ctrl+C to stop.")
        
        # Discovery loop - periodically check for other domains
        discovery_interval = 30  # seconds
        last_discovery_time = 0
        other_domains = []
        
        while True:
            try:
                current_time = time.time()
                
                # Periodically check for new domains
                if current_time - last_discovery_time > discovery_interval:
                    # Discover other domains from the platform
                    print("\nChecking for other domains...")
                    domains_list = domain.get_all_domains()
                    last_discovery_time = current_time
                    
                    if domains_list:
                        # Check for new domains
                        new_domains = []
                        for domain_name in domains_list:
                            if domain_name not in other_domains:
                                new_domains.append(domain_name)
                                other_domains.append(domain_name)
                        
                        # If new domains were found, start interaction
                        if new_domains:
                            print(f"Discovered {len(new_domains)} new domain(s): {', '.join(new_domains)}")
                            
                            # Start interaction with each new domain
                            for target_domain in new_domains:
                                print(f"Starting interaction with {target_domain}...")
                                
                                # Fetch data
                                print(f"Fetching data from {target_domain}...")
                                data = domain.fetch_data_from_domain(target_domain)
                                
                                if data:
                                    domain.data_product.store_external_data(target_domain, data)
                                    print(f"Successfully fetched data from {target_domain}")
                                    
                                    # Start periodic sync
                                    print(f"Starting periodic sync with {target_domain}...")
                                    domain.start_periodic_sync(target_domain, interval_seconds=30)
                            
                            # Show combined data after all interactions
                            if new_domains:
                                combined_data = domain.data_product.get_combined_data_as_string()
                                print(f"Combined data:\n{combined_data}")
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                signal_handler(None, None)

def run_interactive_mode(domain):
    """Run the domain in interactive mode, allowing user commands.
    
    Args:
        domain: The domain client instance
    """
    print("\nInteractive Mode")
    print("=" * 50)
    print("Available commands:")
    print("  list - List all known domains")
    print("  fetch <domain> - Fetch data from a domain")
    print("  sync <domain> - Start periodic sync with a domain")
    print("  stop-sync <domain> - Stop periodic sync with a domain")
    print("  data - Show this domain's data")
    print("  combined - Show combined data")
    print("  help - Show this help")
    print("  exit - Exit the application")
    
    while True:
        try:
            command = input("\nEnter command: ").strip()
            
            if command == "list":
                domains_list = domain.get_all_domains()
                if domains_list:
                    print("\nKnown domains:")
                    for name, info in domains_list.items():
                        print(f"  {name} at {info['host']}:{info['port']}")
                else:
                    print("No other domains found")
                    
            elif command.startswith("fetch "):
                target_domain = command.split(" ", 1)[1].strip()
                print(f"Fetching data from {target_domain}...")
                data = domain.fetch_data_from_domain(target_domain)
                if data:
                    domain.data_product.store_external_data(target_domain, data)
                    print(f"Successfully fetched data from {target_domain}: {data}")
                else:
                    print(f"Failed to fetch data from {target_domain}")
                    
            elif command.startswith("sync "):
                target_domain = command.split(" ", 1)[1].strip()
                print(f"Starting periodic sync with {target_domain}...")
                success = domain.start_periodic_sync(target_domain)
                if success:
                    print(f"Started sync with {target_domain}")
                else:
                    print(f"Failed to start sync with {target_domain}")
                    
            elif command.startswith("stop-sync "):
                target_domain = command.split(" ", 1)[1].strip()
                print(f"Stopping periodic sync with {target_domain}...")
                success = domain.stop_periodic_sync(target_domain)
                if success:
                    print(f"Stopped sync with {target_domain}")
                else:
                    print(f"Failed to stop sync with {target_domain}")
                    
            elif command == "data":
                print(f"\nDomain data:")
                print(domain.data_product.get_data_as_string())
                
            elif command == "combined":
                print(f"\nCombined data:")
                print(domain.data_product.get_combined_data_as_string())
                
            elif command == "help":
                print("\nAvailable commands:")
                print("  list - List all known domains")
                print("  fetch <domain> - Fetch data from a domain")
                print("  sync <domain> - Start periodic sync with a domain")
                print("  stop-sync <domain> - Stop periodic sync with a domain")
                print("  data - Show this domain's data")
                print("  combined - Show combined data")
                print("  help - Show this help")
                print("  exit - Exit the application")
                
            elif command == "exit":
                print("Exiting...")
                break
                
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main entry point for the domain application."""
    # Set up signal handler for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse command line arguments
    args = parse_arguments()
    
    try:
        # Determine domain name
        domain_name = args.domain
        if not domain_name:
            domain_name = get_domain_choice()
            
        # Determine host
        local_ip = args.host
        if not local_ip:
            local_ip = get_ip_choice()
            
        # Determine port
        port = args.port
        if not port:
            port = config.find_available_port()
            if port is None:
                print("Error: Could not find an available port")
                sys.exit(1)
                
        # Run the domain
        run_domain(
            domain_name=domain_name,
            local_ip=local_ip,
            port=port,
            platform_host=args.platform_host,
            platform_port=args.platform_port,
            interactive=args.interactive
        )
        
    except Exception as e:
        print(f"Error running domain: {e}")
        # Clean up
        for domain in domains:
            domain.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()