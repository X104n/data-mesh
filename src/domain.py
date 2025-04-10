"""
Domain module for the simplified data mesh demo.
Provides a general implementation for any domain in the mesh.
Supports running domains in separate processes/computers that can discover and communicate with each other.
"""

from typing import Dict, Optional, Tuple, Callable, List, Any
import threading
import time
import socket
import json
import os
import pickle
import atexit


class DataProduct:
    """A generalized data product that can be used by any domain."""

    def __init__(self, domain_name: str, data: Dict[str, str] = None):
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

    def get_data(self) -> str:
        """Get all data from this domain.
        
        Returns:
            A string representation of the domain's data
        """
        return f"Hello from {self.product_name}! Here's the data: {list(self._data.values())}"
    
    def get_item(self, item_id: str) -> str:
        """Get a specific item by ID.
        
        Args:
            item_id: The ID of the item to retrieve
            
        Returns:
            The requested item or an error message
        """
        if item_id in self._data:
            return self._data[item_id]
        return f"Item {item_id} not found"
    
    def store_external_data(self, source_domain: str, data: str) -> None:
        """Store data received from another domain.
        
        Args:
            source_domain: The name of the domain that provided the data
            data: The data received
        """
        self._external_data[source_domain] = data
        print(f"[{self.domain_name}] Stored data from {source_domain}: {data}")
    
    def get_combined_data(self) -> str:
        """Get a combination of this domain's data and data from other domains.
        
        Returns:
            A string combining all available data
        """
        result = [f"Data from {self.domain_name}: {list(self._data.values())}"]
        
        for domain, data in self._external_data.items():
            result.append(f"Data from {domain}: {data}")
            
        return "\n".join(result)


# Define the registry file path - will be in the user's home directory
REGISTRY_FILE = os.path.join(os.path.expanduser("~"), ".data_mesh_registry")

def save_domain_registry(registry: Dict[str, Dict[str, Any]]) -> None:
    """Save the domain registry to a file.
    
    Args:
        registry: The registry to save
    """
    try:
        with open(REGISTRY_FILE, 'wb') as f:
            pickle.dump(registry, f)
    except Exception as e:
        print(f"Error saving registry: {e}")

def load_domain_registry() -> Dict[str, Dict[str, Any]]:
    """Load the domain registry from a file.
    
    Returns:
        The loaded registry or an empty dict if the file doesn't exist
    """
    try:
        if os.path.exists(REGISTRY_FILE):
            with open(REGISTRY_FILE, 'rb') as f:
                return pickle.load(f)
    except Exception as e:
        print(f"Error loading registry: {e}")
    return {}


class DomainController:
    """A generalized controller for any domain in the data mesh."""
    
    # Shared registry for all domain controllers
    global_registry = load_domain_registry()
    
    def __init__(self, domain_name: str, host: str, port: int, initial_data: Dict[str, str] = None):
        """Initialize a domain controller.
        
        Args:
            domain_name: The name of this domain
            host: The host to bind the server to (IP address)
            port: The port to bind the server to
            initial_data: Initial data dictionary for the data product (optional)
        """
        self.domain_name = domain_name
        self.host = host
        self.port = port
        self.data_product = DataProduct(domain_name, initial_data)
        
        # Set up server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = False
        self.server_thread = None
        
        # For periodic syncs
        self.sync_threads = []
        self.domain_registry = {}
        
        # Register this domain in the global registry
        self._register_self()
        
        # Register cleanup on exit
        atexit.register(self.stop)
    
    def start(self) -> None:
        """Start the domain server."""
        # Bind to all interfaces on the specified port
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        self.running = True
        
        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        print(f"[{self.domain_name}] Controller started on {self.host}:{self.port}")
    
    def stop(self) -> None:
        """Stop the domain server and all sync threads."""
        self.running = False
        
        # Close the server socket
        if hasattr(self, 'server_socket'):
            self.server_socket.close()
            
        # Stop all sync threads
        for thread in self.sync_threads:
            thread['running'] = False
            
        print(f"[{self.domain_name}] Controller stopped")
    
    def _run_server(self) -> None:
        """Run the server loop, accepting connections and handling messages."""
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                if self.running:  # Only print error if we're supposed to be running
                    print(f"[{self.domain_name}] Server error: {e}")
    
    def _handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]) -> None:
        """Handle an individual client connection.
        
        Args:
            client_socket: The client socket object
            client_address: Tuple of (host, port) for the client
        """
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                print(f"[{self.domain_name}] Received: '{data}' from {client_address}")
                response = self._process_message(data)
                if response:
                    client_socket.send(response.encode('utf-8'))
        except Exception as e:
            print(f"[{self.domain_name}] Error handling client: {e}")
        finally:
            client_socket.close()
    
    def _register_self(self) -> None:
        """Register this domain in the global registry."""
        DomainController.global_registry[self.domain_name] = {
            "host": self.host,
            "port": self.port,
            "timestamp": time.time()
        }
        save_domain_registry(DomainController.global_registry)
        print(f"[{self.domain_name}] Registered in global registry")

    def _process_message(self, message: str) -> str:
        """Process incoming messages and return a response.
        
        Args:
            message: The message to process
            
        Returns:
            A response string
        """
        try:
            # Try to parse as JSON first (for command messages)
            try:
                cmd = json.loads(message)
                if isinstance(cmd, dict) and "command" in cmd:
                    return self._process_command(cmd)
            except json.JSONDecodeError:
                # Not JSON, treat as simple command
                pass
            
            # Log the request
            self._log_exchange("client", self.domain_name, "request")
            
            # Process simple commands
            if message.strip().lower() == "get_data":
                response = self.data_product.get_data()
            elif message.startswith("get_item:"):
                item_id = message.split(":", 1)[1].strip()
                response = self.data_product.get_item(item_id)
            elif message.strip().lower() == "get_combined_data":
                response = self.data_product.get_combined_data()
            elif message.strip().lower() == "get_registry":
                # Return the registry information
                response = json.dumps(DomainController.global_registry)
            else:
                response = f"Unknown command: {message}"
            
            # Log the response
            self._log_exchange(self.domain_name, "client", "response")
            return response
            
        except Exception as e:
            return f"Error: {str(e)}"
            
    def _process_command(self, cmd: Dict[str, Any]) -> str:
        """Process a command received as JSON.
        
        Args:
            cmd: The command dictionary
            
        Returns:
            A response string
        """
        command = cmd["command"]
        
        if command == "register_domain":
            # Another domain is registering with this one
            domain_name = cmd.get("domain_name")
            host = cmd.get("host")
            port = cmd.get("port")
            
            if domain_name and host and port:
                self.register_domain(domain_name, host, port)
                return json.dumps({"status": "success", "message": f"Registered {domain_name}"})
            else:
                return json.dumps({"status": "error", "message": "Missing required parameters"})
                
        elif command == "ping":
            # Simple ping to check if domain is alive
            return json.dumps({
                "status": "success", 
                "domain": self.domain_name,
                "time": time.time()
            })
        
        elif command == "broadcast_discovery":
            # Handle broadcast discovery requests
            domain_name = cmd.get("domain_name")
            host = cmd.get("host")
            port = cmd.get("port")
            
            if domain_name and host and port:
                self.register_domain(domain_name, host, port)
                # Reply with our own information
                return json.dumps({
                    "status": "success",
                    "domain_name": self.domain_name,
                    "host": self.host,
                    "port": self.port
                })
            
        return json.dumps({"status": "error", "message": f"Unknown command: {command}"})
    
    def send_message(self, target_domain: str, host: str, port: int, message: str) -> Optional[str]:
        """Send a message to another domain.
        
        Args:
            target_domain: The name of the target domain
            host: The host of the target domain
            port: The port of the target domain
            message: The message to send
            
        Returns:
            The response from the target domain, or None if there was an error
        """
        try:
            self._log_exchange(self.domain_name, target_domain, "request")
            
            # Create a client socket for this request
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            client_socket.send(message.encode('utf-8'))
            
            # Wait for response with a timeout
            client_socket.settimeout(5)
            response = client_socket.recv(1024).decode('utf-8')
            
            print(f"[{self.domain_name}] Sent: '{message}' to {target_domain}, Received: '{response}'")
            
            self._log_exchange(target_domain, self.domain_name, "response")
            return response
            
        except Exception as e:
            print(f"[{self.domain_name}] Error sending message to {target_domain}: {e}")
            return None
        finally:
            if 'client_socket' in locals():
                client_socket.close()
    
    def fetch_data_from_domain(self, target_domain: str, host: str, port: int) -> bool:
        """Fetch data from another domain and store it.
        
        Args:
            target_domain: The name of the target domain
            host: The host of the target domain
            port: The port of the target domain
            
        Returns:
            True if successful, False otherwise
        """
        response = self.send_message(target_domain, host, port, "get_data")
        if response:
            self.data_product.store_external_data(target_domain, response)
            return True
        return False
    
    def register_domain(self, domain_name: str, host: str, port: int) -> None:
        """Register another domain in this controller's registry.
        
        Args:
            domain_name: The name of the domain to register
            host: The host of the domain
            port: The port of the domain
        """
        # Check if this domain is already registered with the same details
        if domain_name in self.domain_registry:
            existing_host, existing_port = self.domain_registry[domain_name]
            if existing_host == host and existing_port == port:
                # Domain already registered with the same details, no need to register again
                return
                
        # Register the domain
        self.domain_registry[domain_name] = (host, port)
        print(f"[{self.domain_name}] Registered domain {domain_name} at {host}:{port}")
        
        # Also notify the other domain about this domain if it's not already done
        try:
            # Check if the other domain needs to be notified
            # First, check if we've already successfully notified this domain
            if f"notified_{domain_name}" not in self.__dict__:
                self._notify_domain(domain_name, host, port)
                # Mark this domain as notified to prevent future notifications
                self.__dict__[f"notified_{domain_name}"] = True
        except Exception as e:
            print(f"[{self.domain_name}] Error registering with {domain_name}: {e}")
            
    def _notify_domain(self, domain_name: str, host: str, port: int) -> None:
        """Notify another domain about this domain.
        
        Args:
            domain_name: The name of the domain to notify
            host: The host of the domain
            port: The port of the domain
        """
        # Check if this domain is already in the global registry
        registry = load_domain_registry()
        already_registered = False
        
        command = {
            "command": "register_domain",
            "domain_name": self.domain_name,
            "host": self.host,
            "port": self.port
        }
        
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            client_socket.send(json.dumps(command).encode('utf-8'))
            
            # Wait for response with a timeout
            client_socket.settimeout(5)
            response = client_socket.recv(1024).decode('utf-8')
            
            try:
                result = json.loads(response)
                if result.get("status") == "success":
                    print(f"[{self.domain_name}] Successfully registered with {domain_name}")
                else:
                    print(f"[{self.domain_name}] Failed to register with {domain_name}: {result.get('message')}")
            except json.JSONDecodeError:
                print(f"[{self.domain_name}] Received non-JSON response from {domain_name}: {response}")
                
        except Exception as e:
            print(f"[{self.domain_name}] Error notifying {domain_name}: {e}")
        finally:
            if 'client_socket' in locals():
                client_socket.close()
    
    def broadcast_discovery(self, target_ips=None) -> None:
        """Broadcast discovery to find other domains across different machines.
        
        Args:
            target_ips: List of IP addresses to broadcast to (None = use default range)
        """
        if target_ips is None:
            # Default to common IP ranges on most networks - modify as needed
            target_ips = [
                "10.0.3.4", "10.0.3.5", "10.0.3.6", "10.0.3.7"
            ]
        
        # Exclude our own IP
        target_ips = [ip for ip in target_ips if ip != self.host]
        
        command = {
            "command": "broadcast_discovery",
            "domain_name": self.domain_name,
            "host": self.host,
            "port": self.port
        }
        
        for ip in target_ips:
            # Try common ports for potential domains
            for port in range(9000, 9100):
                try:
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.settimeout(0.3)  # Very short timeout for scanning
                    client_socket.connect((ip, port))
                    client_socket.send(json.dumps(command).encode('utf-8'))
                    
                    # Wait for response with a short timeout
                    response = client_socket.recv(1024).decode('utf-8')
                    
                    try:
                        result = json.loads(response)
                        if result.get("status") == "success":
                            domain_name = result.get("domain_name")
                            host = result.get("host")
                            port = result.get("port")
                            
                            if domain_name and host and port:
                                self.register_domain(domain_name, host, port)
                                print(f"[{self.domain_name}] Discovered domain {domain_name} at {host}:{port}")
                    except json.JSONDecodeError:
                        continue
                        
                except (socket.timeout, ConnectionRefusedError, OSError):
                    # These errors are expected when scanning - just continue
                    pass
                except Exception as e:
                    # Other errors might be worth logging
                    print(f"Error during broadcast to {ip}:{port}: {e}")
                finally:
                    if 'client_socket' in locals():
                        client_socket.close()
    
    def discover_domains(self) -> Dict[str, Tuple[str, int]]:
        """Discover available domains from the global registry and network broadcast.
        
        Returns:
            A dictionary of domain names to (host, port) tuples
        """
        # First broadcast discovery to find domains on other machines
        self.broadcast_discovery()
        
        # Then load the latest registry
        registry = load_domain_registry()
        current_time = time.time()
        
        # Update our local registry without triggering notifications
        for domain_name, info in registry.items():
            if domain_name != self.domain_name:
                # Add directly to registry without triggering notifications
                if domain_name not in self.domain_registry:
                    # Verify domain is recent (within last hour)
                    if current_time - info.get("timestamp", 0) < 3600:
                        self.domain_registry[domain_name] = (info["host"], info["port"])
                        print(f"Discovered domain {domain_name} at {info['host']}:{info['port']}")
                        
                        # Now try to notify this domain, but only once
                        try:
                            if info["host"] != self.host or info["port"] != self.port:
                                self._notify_domain(domain_name, info["host"], info["port"])
                        except Exception as e:
                            print(f"Could not connect to discovered domain {domain_name}: {e}")
                
        return self.domain_registry
    
    def start_periodic_sync(self, target_domain: str, interval_seconds: int = 60) -> None:
        """Start a periodic sync with another domain.
        
        Args:
            target_domain: The name of the domain to sync with
            interval_seconds: The interval between syncs in seconds
        """
        # Avoid starting multiple syncs with the same domain
        if hasattr(self, f"sync_running_{target_domain}") and getattr(self, f"sync_running_{target_domain}"):
            print(f"[{self.domain_name}] Sync already running with {target_domain}")
            return
            
        # First check our local registry
        if target_domain not in self.domain_registry:
            print(f"[{self.domain_name}] Cannot sync with unknown domain {target_domain}")
            return
            
        host, port = self.domain_registry[target_domain]
        
        # Create a thread state dictionary so we can control it later
        thread_state = {'running': True}
        self.sync_threads.append(thread_state)
        
        # Set flag to indicate sync is running
        setattr(self, f"sync_running_{target_domain}", True)
        
        def sync_job():
            while thread_state['running']:
                try:
                    print(f"[{self.domain_name}] Syncing with {target_domain}...")
                    self.fetch_data_from_domain(target_domain, host, port)
                except Exception as e:
                    print(f"[{self.domain_name}] Error syncing with {target_domain}: {e}")
                time.sleep(interval_seconds)
        
        sync_thread = threading.Thread(target=sync_job)
        sync_thread.daemon = True
        sync_thread.start()
        
        print(f"[{self.domain_name}] Started periodic sync with {target_domain} (interval: {interval_seconds}s)")
    
    def _log_exchange(self, source: str, target: str, message_type: str) -> None:
        """Log a data exchange.
        
        Args:
            source: The source of the exchange
            target: The target of the exchange
            message_type: The type of message being exchanged
        """
        print(f"Data exchange: {source} -> {target}, type: {message_type}")