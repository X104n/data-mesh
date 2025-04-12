"""
Mesh SDK for the data mesh platform.
Provides a simple interface for domains to interact with the platform.
"""

import socket
import json
import threading
import time
from typing import Dict, Any, Optional, List, Callable

class MeshSDK:
    """SDK for domain teams to interact with the platform."""
    
    def __init__(self, domain_name: str, host: str, port: int, platform_host: str, platform_port: int):
        """Initialize the mesh SDK.
        
        Args:
            domain_name: The name of this domain
            host: The host that this domain is running on
            port: The port that this domain is running on
            platform_host: The host of the platform server
            platform_port: The port of the platform server
        """
        self.domain_name = domain_name
        self.host = host
        self.port = port
        self.platform_host = platform_host
        self.platform_port = platform_port
        
        # For domain server
        self.server_socket = None
        self.running = False
        self.server_thread = None
        
        # Command handlers
        self.command_handlers = {}
        
        # Add default command handlers
        self._add_default_handlers()
    
    def register_command_handler(self, command: str, handler: Callable[[Dict[str, Any]], str]) -> None:
        """Register a handler for a specific command.
        
        Args:
            command: The command to handle
            handler: The function to handle the command
        """
        self.command_handlers[command] = handler
    
    def _add_default_handlers(self) -> None:
        """Add default command handlers."""
        self.register_command_handler("ping", self._handle_ping)
        self.register_command_handler("get_data", self._handle_get_data)
    
    def _handle_ping(self, cmd: Dict[str, Any]) -> str:
        """Handle a ping command.
        
        Args:
            cmd: The command dictionary
            
        Returns:
            A response string
        """
        return json.dumps({
            "status": "success",
            "domain": self.domain_name,
            "time": time.time()
        })
    
    def _handle_get_data(self, cmd: Dict[str, Any]) -> str:
        """Handle a get_data command - subclasses should override this.
        
        Args:
            cmd: The command dictionary
            
        Returns:
            A response string
        """
        return json.dumps({
            "status": "success",
            "message": f"No data available for {self.domain_name}"
        })
    
    def start(self) -> bool:
        """Start the SDK server to handle incoming requests.
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.running:
            return True
            
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(5)
            
            self.running = True
            self.server_thread = threading.Thread(target=self._run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            print(f"[{self.domain_name}] SDK server started on {self.host}:{self.port}")
            
            # Register with the platform
            success = self.register_with_platform()
            if not success:
                print(f"[{self.domain_name}] Warning: Failed to register with platform")
                
            return True
        except Exception as e:
            print(f"[{self.domain_name}] Error starting SDK server: {e}")
            return False
    
    def stop(self) -> None:
        """Stop the SDK server."""
        self.running = False
        
        if self.server_socket:
            self.server_socket.close()
            
        if self.server_thread:
            self.server_thread.join(timeout=2)
            
        print(f"[{self.domain_name}] SDK server stopped")
    
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
    
    def _handle_client(self, client_socket: socket.socket, client_address: tuple) -> None:
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
            # Parse message as JSON
            try:
                cmd = json.loads(message)
                if isinstance(cmd, dict) and "command" in cmd:
                    command = cmd["command"]
                    if command in self.command_handlers:
                        return self.command_handlers[command](cmd)
                    else:
                        return json.dumps({
                            "status": "error",
                            "message": f"Unknown command: {command}"
                        })
            except json.JSONDecodeError:
                # Simple text command
                if message.strip() in self.command_handlers:
                    return self.command_handlers[message.strip()]({
                        "command": message.strip()
                    })
                else:
                    return json.dumps({
                        "status": "error",
                        "message": f"Unknown command: {message}"
                    })
                
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Error processing message: {str(e)}"
            })
    
    def register_with_platform(self) -> bool:
        """Register this domain with the platform.
        
        Returns:
            True if registration was successful, False otherwise
        """
        message = {
            "command": "register_domain",
            "domain_name": self.domain_name,
            "host": self.host,
            "port": self.port
        }
        
        response = self._send_to_platform(message)
        
        if response and response.get("status") == "success":
            print(f"[{self.domain_name}] Registered with platform")
            return True
        else:
            error_msg = response.get("message", "Unknown error") if response else "No response"
            print(f"[{self.domain_name}] Failed to register with platform: {error_msg}")
            return False
    
    def get_all_domains(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """Get information about all registered domains.
        
        Returns:
            Dictionary of domain information or None if request failed
        """
        message = {
            "command": "get_domains",
            "exclude_domain": self.domain_name  # Exclude ourselves
        }
        
        response = self._send_to_platform(message)
        
        if response and response.get("status") == "success":
            return response.get("domains", {})
        else:
            error_msg = response.get("message", "Unknown error") if response else "No response"
            print(f"[{self.domain_name}] Failed to get domains: {error_msg}")
            return None
    
    def get_domain_info(self, target_domain: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific domain.
        
        Args:
            target_domain: The name of the domain to query
            
        Returns:
            Domain information or None if not found
        """
        message = {
            "command": "get_domain",
            "domain_name": target_domain
        }
        
        response = self._send_to_platform(message)
        
        if response and response.get("status") == "success":
            return response.get("domain")
        else:
            error_msg = response.get("message", "Unknown error") if response else "No response"
            print(f"[{self.domain_name}] Failed to get domain info: {error_msg}")
            return None
    
    def _send_to_platform(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a message to the platform server.
        
        Args:
            message: The message to send
            
        Returns:
            The response from the platform, or None if there was an error
        """
        try:
            # Create a client socket for this request
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.platform_host, self.platform_port))
            client_socket.send(json.dumps(message).encode('utf-8'))
            
            # Wait for response with a timeout
            client_socket.settimeout(5)
            response = client_socket.recv(1024).decode('utf-8')
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                print(f"[{self.domain_name}] Received non-JSON response: {response}")
                return None
                
        except Exception as e:
            print(f"[{self.domain_name}] Error sending message to platform: {e}")
            return None
        finally:
            if 'client_socket' in locals():
                client_socket.close()
    
    def send_to_domain(self, target_domain: str, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a message to another domain.
        
        Args:
            target_domain: The name of the target domain
            message: The message to send
            
        Returns:
            The response from the domain, or None if there was an error
        """
        # First get domain info from the platform
        domain_info = self.get_domain_info(target_domain)
        
        if not domain_info:
            print(f"[{self.domain_name}] Unknown domain: {target_domain}")
            return None
            
        host = domain_info["host"]
        port = domain_info["port"]
        
        try:
            # Create a client socket for this request
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            client_socket.send(json.dumps(message).encode('utf-8'))
            
            # Wait for response with a timeout
            client_socket.settimeout(5)
            response = client_socket.recv(1024).decode('utf-8')
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                print(f"[{self.domain_name}] Received non-JSON response from {target_domain}: {response}")
                return None
                
        except Exception as e:
            print(f"[{self.domain_name}] Error sending message to {target_domain}: {e}")
            return None
        finally:
            if 'client_socket' in locals():
                client_socket.close()
    
    def fetch_data_from_domain(self, target_domain: str) -> Optional[str]:
        """Fetch data from another domain.
        
        Args:
            target_domain: The name of the domain to fetch data from
            
        Returns:
            The fetched data or None if there was an error
        """
        response = self.send_to_domain(target_domain, {
            "command": "get_data"
        })
        
        if response and response.get("status") == "success":
            return response.get("data")
        else:
            error_msg = response.get("message", "Unknown error") if response else "No response"
            print(f"[{self.domain_name}] Failed to fetch data from {target_domain}: {error_msg}")
            return None