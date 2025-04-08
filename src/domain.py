"""
Domain module for the simplified data mesh demo.
Provides a general implementation for any domain in the mesh.
"""

from typing import Dict, Optional, Tuple, Callable, List
import threading
import time
import socket


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


class DomainController:
    """A generalized controller for any domain in the data mesh."""
    
    def __init__(self, domain_name: str, host: str, port: int, initial_data: Dict[str, str] = None):
        """Initialize a domain controller.
        
        Args:
            domain_name: The name of this domain
            host: The host to bind the server to
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
    
    def start(self) -> None:
        """Start the domain server."""
        self.server_socket.bind((self.host, self.port))
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
    
    def _process_message(self, message: str) -> str:
        """Process incoming messages and return a response.
        
        Args:
            message: The message to process
            
        Returns:
            A response string
        """
        try:
            # Log the request
            self._log_exchange("client", self.domain_name, "request")
            
            # Process commands
            if message.strip().lower() == "get_data":
                response = self.data_product.get_data()
            elif message.startswith("get_item:"):
                item_id = message.split(":", 1)[1].strip()
                response = self.data_product.get_item(item_id)
            elif message.strip().lower() == "get_combined_data":
                response = self.data_product.get_combined_data()
            else:
                response = f"Unknown command: {message}"
            
            # Log the response
            self._log_exchange(self.domain_name, "client", "response")
            return response
            
        except Exception as e:
            return f"Error: {str(e)}"
    
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
        self.domain_registry[domain_name] = (host, port)
        print(f"[{self.domain_name}] Registered domain {domain_name} at {host}:{port}")
    
    def start_periodic_sync(self, target_domain: str, interval_seconds: int = 60) -> None:
        """Start a periodic sync with another domain.
        
        Args:
            target_domain: The name of the domain to sync with
            interval_seconds: The interval between syncs in seconds
        """
        if target_domain not in self.domain_registry:
            print(f"[{self.domain_name}] Cannot sync with unknown domain {target_domain}")
            return
            
        host, port = self.domain_registry[target_domain]
        
        # Create a thread state dictionary so we can control it later
        thread_state = {'running': True}
        self.sync_threads.append(thread_state)
        
        def sync_job():
            while thread_state['running']:
                print(f"[{self.domain_name}] Syncing with {target_domain}...")
                self.fetch_data_from_domain(target_domain, host, port)
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