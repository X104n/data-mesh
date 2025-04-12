"""
Discovery module for the data mesh platform.
Handles domain discovery across the network.
"""

import socket
import json
import threading
import time
from typing import List, Dict, Any, Optional

from platform.registry import get_registry

class DiscoveryService:
    """Service for discovering domains across the network."""
    
    def __init__(self):
        """Initialize the discovery service."""
        self.registry = get_registry()
        self.running = False
        self.discovery_thread = None
    
    def start(self) -> None:
        """Start the discovery service."""
        if self.running:
            return
            
        self.running = True
        self.discovery_thread = threading.Thread(target=self._run_discovery)
        self.discovery_thread.daemon = True
        self.discovery_thread.start()
        print("[Discovery] Service started")
    
    def stop(self) -> None:
        """Stop the discovery service."""
        self.running = False
        if self.discovery_thread:
            self.discovery_thread.join(timeout=2)
        print("[Discovery] Service stopped")
    
    def _run_discovery(self) -> None:
        """Run the discovery process periodically."""
        while self.running:
            try:
                self._scan_network()
            except Exception as e:
                print(f"[Discovery] Error during network scan: {e}")
            time.sleep(60)  # Scan once per minute
    
    def _scan_network(self) -> None:
        """Scan the network for potential domains."""
        # Default to common IP ranges on most networks - modify as needed
        target_ips = [
            "10.0.3.4", "10.0.3.5", "10.0.3.6", "10.0.3.7"
        ]
        
        command = {
            "command": "ping",
            "timestamp": time.time()
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
                            domain_name = result.get("domain")
                            
                            if domain_name:
                                # Register the domain if it responded properly
                                self.registry.register_domain(domain_name, ip, port)
                                print(f"[Discovery] Found domain {domain_name} at {ip}:{port}")
                    except json.JSONDecodeError:
                        continue
                        
                except (socket.timeout, ConnectionRefusedError, OSError):
                    # These errors are expected when scanning - just continue
                    pass
                except Exception as e:
                    # Other errors might be worth logging
                    print(f"[Discovery] Error during scan of {ip}:{port}: {e}")
                finally:
                    if 'client_socket' in locals():
                        client_socket.close()
    
    def discover_domain(self, domain_name: str) -> Optional[Dict[str, Any]]:
        """Discover a specific domain by name.
        
        Args:
            domain_name: The name of the domain to discover
            
        Returns:
            Domain information if found, None otherwise
        """
        # First check registry
        domain_info = self.registry.get_domain(domain_name)
        if domain_info:
            return domain_info
            
        # If not found, trigger a network scan to find it
        self._scan_network()
        
        # Check again after scanning
        return self.registry.get_domain(domain_name)

# Singleton instance
_discovery_instance = None

def get_discovery_service() -> DiscoveryService:
    """Get the singleton instance of the discovery service.
    
    Returns:
        The discovery service instance
    """
    global _discovery_instance
    if _discovery_instance is None:
        _discovery_instance = DiscoveryService()
    return _discovery_instance