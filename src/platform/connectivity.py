"""
Connectivity module for the data mesh platform.
Handles communication between domains.
"""

import socket
import json
import threading
from typing import Dict, Any, Optional, Callable, List, Tuple

from platform.registry import get_registry
from platform.discovery import get_discovery_service

class MessagingService:
    """Service for handling messaging between domains."""
    
    def __init__(self, host: str, port: int):
        """Initialize the messaging service.
        
        Args:
            host: The host to bind the server to
            port: The port to bind the server to
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.server_thread = None
        self.registry = get_registry()
        self.discovery = get_discovery_service()
        
        # Command handlers
        self.command_handlers = {
            "register_domain": self._handle_register_domain,
            "ping": self._handle_ping,
            "get_domains": self._handle_get_domains,
            "get_domain": self._handle_get_domain,
        }
    
    def start(self) -> None:
        """Start the messaging service."""
        if self.running:
            return
            
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        
        self.running = True
        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        print(f"[Messaging] Service started on {self.host}:{self.port}")
    
    def stop(self) -> None:
        """Stop the messaging service."""
        self.running = False
        
        if self.server_socket:
            self.server_socket.close()
            
        if self.server_thread:
            self.server_thread.join(timeout=2)
            
        print("[Messaging] Service stopped")
    
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
                    print(f"[Messaging] Server error: {e}")
    
    def _handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]) -> None:
        """Handle an individual client connection.
        
        Args:
            client_socket: The client socket object
            client_address: Tuple of (host, port) for the client
        """
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                print(f"[Messaging] Received: '{data}' from {client_address}")
                response = self._process_message(data)
                if response:
                    client_socket.send(response.encode('utf-8'))
        except Exception as e:
            print(f"[Messaging] Error handling client: {e}")
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
                # Not JSON, treat as simple text command
                return json.dumps({
                    "status": "error",
                    "message": "Invalid command format. Expected JSON."
                })
                
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Error processing message: {str(e)}"
            })
    
    def _handle_register_domain(self, cmd: Dict[str, Any]) -> str:
        """Handle a domain registration command.
        
        Args:
            cmd: The command dictionary
            
        Returns:
            A response string
        """
        domain_name = cmd.get("domain_name")
        host = cmd.get("host")
        port = cmd.get("port")
        
        if domain_name and host and port:
            success = self.registry.register_domain(domain_name, host, port)
            if success:
                return json.dumps({
                    "status": "success",
                    "message": f"Registered domain {domain_name}"
                })
            else:
                return json.dumps({
                    "status": "error",
                    "message": f"Failed to register domain {domain_name}"
                })
        else:
            return json.dumps({
                "status": "error",
                "message": "Missing required parameters: domain_name, host, port"
            })
    
    def _handle_ping(self, cmd: Dict[str, Any]) -> str:
        """Handle a ping command.
        
        Args:
            cmd: The command dictionary
            
        Returns:
            A response string
        """
        return json.dumps({
            "status": "success",
            "service": "platform",
            "time": cmd.get("timestamp", 0)
        })
    
    def _handle_get_domains(self, cmd: Dict[str, Any]) -> str:
        """Handle a get_domains command.
        
        Args:
            cmd: The command dictionary
            
        Returns:
            A response string
        """
        exclude_domain = cmd.get("exclude_domain")
        domains = self.registry.get_domains(exclude_domain)
        
        return json.dumps({
            "status": "success",
            "domains": domains
        })
    
    def _handle_get_domain(self, cmd: Dict[str, Any]) -> str:
        """Handle a get_domain command.
        
        Args:
            cmd: The command dictionary
            
        Returns:
            A response string
        """
        domain_name = cmd.get("domain_name")
        
        if not domain_name:
            return json.dumps({
                "status": "error",
                "message": "Missing required parameter: domain_name"
            })
            
        domain_info = self.registry.get_domain(domain_name)
        
        if domain_info:
            return json.dumps({
                "status": "success",
                "domain": domain_info
            })
        else:
            return json.dumps({
                "status": "error",
                "message": f"Domain {domain_name} not found"
            })
    
    def send_message(self, target_host: str, target_port: int, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a message to a specific host and port.
        
        Args:
            target_host: The host to send the message to
            target_port: The port to send the message to
            message: The message to send
            
        Returns:
            The response from the target, or None if there was an error
        """
        try:
            # Create a client socket for this request
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((target_host, target_port))
            client_socket.send(json.dumps(message).encode('utf-8'))
            
            # Wait for response with a timeout
            client_socket.settimeout(5)
            response = client_socket.recv(1024).decode('utf-8')
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                print(f"[Messaging] Received non-JSON response: {response}")
                return None
                
        except Exception as e:
            print(f"[Messaging] Error sending message to {target_host}:{target_port}: {e}")
            return None
        finally:
            if 'client_socket' in locals():
                client_socket.close()
    
    def send_to_domain(self, domain_name: str, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a message to a specific domain.
        
        Args:
            domain_name: The name of the target domain
            message: The message to send
            
        Returns:
            The response from the domain, or None if there was an error
        """
        # First check if we know this domain
        domain_info = self.registry.get_domain(domain_name)
        
        # If not, try to discover it
        if not domain_info:
            domain_info = self.discovery.discover_domain(domain_name)
            
        if not domain_info:
            print(f"[Messaging] Unknown domain: {domain_name}")
            return None
            
        host = domain_info["host"]
        port = domain_info["port"]
        
        return self.send_message(host, port, message)