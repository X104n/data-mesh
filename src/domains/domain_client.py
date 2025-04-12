"""
Domain Client module for domain teams.
Extends the SDK to provide domain-specific functionality.
"""

import json
import time
import threading
from typing import Dict, Any, Optional, List, Callable

from platform.mesh_sdk import MeshSDK
from domains.data_product import DataProduct

class DomainClient(MeshSDK):
    """Client for domain teams to interact with the data mesh."""
    
    def __init__(self, domain_name: str, host: str, port: int, platform_host: str, platform_port: int, 
                 data_product: DataProduct = None, initial_data: Dict[str, Any] = None):
        """Initialize a domain client.
        
        Args:
            domain_name: The name of this domain
            host: The host that this domain is running on
            port: The port that this domain is running on
            platform_host: The host of the platform server
            platform_port: The port of the platform server
            data_product: An optional data product instance
            initial_data: Initial data for the data product (if no data_product provided)
        """
        super().__init__(domain_name, host, port, platform_host, platform_port)
        
        # Create or use provided data product
        if data_product:
            self.data_product = data_product
        else:
            self.data_product = DataProduct(domain_name, initial_data)
        
        # Override the default handler for get_data
        self.register_command_handler("get_data", self._handle_domain_get_data)
        
        # Add domain-specific command handlers
        self.register_command_handler("get_item", self._handle_get_item)
        self.register_command_handler("get_combined_data", self._handle_get_combined_data)
        
        # For periodic syncs
        self.sync_threads = []
    
    def _handle_domain_get_data(self, cmd: Dict[str, Any]) -> str:
        """Handle a get_data command with this domain's data.
        
        Args:
            cmd: The command dictionary
            
        Returns:
            A response string
        """
        data = self.data_product.get_data()
        
        return json.dumps({
            "status": "success",
            "domain": self.domain_name,
            "data": self.data_product.get_data_as_string()  # Use string representation for compatibility
        })
    
    def _handle_get_item(self, cmd: Dict[str, Any]) -> str:
        """Handle a get_item command.
        
        Args:
            cmd: The command dictionary
            
        Returns:
            A response string
        """
        item_id = cmd.get("item_id")
        
        if not item_id:
            return json.dumps({
                "status": "error",
                "message": "Missing required parameter: item_id"
            })
            
        item = self.data_product.get_item(item_id)
        
        if item is not None:
            return json.dumps({
                "status": "success",
                "item": item
            })
        else:
            return json.dumps({
                "status": "error",
                "message": f"Item {item_id} not found"
            })
    
    def _handle_get_combined_data(self, cmd: Dict[str, Any]) -> str:
        """Handle a get_combined_data command.
        
        Args:
            cmd: The command dictionary
            
        Returns:
            A response string
        """
        return json.dumps({
            "status": "success",
            "data": self.data_product.get_combined_data_as_string()
        })
    
    def start_periodic_sync(self, target_domain: str, interval_seconds: int = 60) -> bool:
        """Start a periodic sync with another domain.
        
        Args:
            target_domain: The name of the domain to sync with
            interval_seconds: The interval between syncs in seconds
            
        Returns:
            True if sync was started successfully, False otherwise
        """
        # Avoid starting multiple syncs with the same domain
        if hasattr(self, f"sync_running_{target_domain}") and getattr(self, f"sync_running_{target_domain}"):
            print(f"[{self.domain_name}] Sync already running with {target_domain}")
            return False
            
        # Create a thread state dictionary so we can control it later
        thread_state = {'running': True}
        self.sync_threads.append(thread_state)
        
        # Set flag to indicate sync is running
        setattr(self, f"sync_running_{target_domain}", True)
        
        def sync_job():
            while thread_state['running']:
                try:
                    print(f"[{self.domain_name}] Syncing with {target_domain}...")
                    data = self.fetch_data_from_domain(target_domain)
                    if data:
                        self.data_product.store_external_data(target_domain, data)
                        print(f"[{self.domain_name}] Successfully synced with {target_domain}")
                    else:
                        print(f"[{self.domain_name}] Failed to sync with {target_domain}")
                except Exception as e:
                    print(f"[{self.domain_name}] Error syncing with {target_domain}: {e}")
                time.sleep(interval_seconds)
        
        sync_thread = threading.Thread(target=sync_job)
        sync_thread.daemon = True
        sync_thread.start()
        
        print(f"[{self.domain_name}] Started periodic sync with {target_domain} (interval: {interval_seconds}s)")
        return True
    
    def stop_periodic_sync(self, target_domain: str) -> bool:
        """Stop a periodic sync with another domain.
        
        Args:
            target_domain: The name of the domain to stop syncing with
            
        Returns:
            True if sync was stopped successfully, False otherwise
        """
        sync_attr = f"sync_running_{target_domain}"
        
        if hasattr(self, sync_attr) and getattr(self, sync_attr):
            setattr(self, sync_attr, False)
            print(f"[{self.domain_name}] Stopped periodic sync with {target_domain}")
            return True
        else:
            print(f"[{self.domain_name}] No active sync with {target_domain}")
            return False
    
    def stop(self) -> None:
        """Stop the client, including all sync threads."""
        # Stop all sync threads
        for thread in self.sync_threads:
            thread['running'] = False
        
        # Stop the SDK server
        super().stop()