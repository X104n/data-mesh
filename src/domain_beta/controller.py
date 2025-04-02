"""
Controller module for the Beta domain.
Handles network communication and business logic.
"""

from typing import Tuple, Optional
import time
import threading

from domain_beta.data_product import BetaDataProduct
from infra.socket_manager import SocketServer, SocketClient
from infra.governance import verify_message, log_data_exchange


class BetaController:
    """Controller for the Beta domain."""

    def __init__(self, host: str, port: int):
        """Initialize the Beta controller.

        Args:
            host: The host to bind the server to
            port: The port to bind the server to
        """
        self.domain_name = "domain_beta"
        self.host = host
        self.port = port
        self.data_product = BetaDataProduct()
        self.server = SocketServer(host, port, self.domain_name)
        self.client = SocketClient(self.domain_name)
        self.sync_thread = None
        self.sync_running = False

        # Set up message handling
        self.server.set_message_handler(self.handle_message)

    def start(self) -> None:
        """Start the Beta domain server."""
        self.server.start()
        print(f"[{self.domain_name}] Controller started")

    def stop(self) -> None:
        """Stop the Beta domain server."""
        self.server.stop()
        self.sync_running = False
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=1)
        print(f"[{self.domain_name}] Controller stopped")

    def handle_message(self, message: str, client_address: Tuple[str, int]) -> str:
        """Handle incoming messages from clients.

        Args:
            message: The message received from the client
            client_address: The (host, port) tuple of the client

        Returns:
            A response message to send back to the client
        """
        try:
            verify_message(message)
            log_data_exchange("client", self.domain_name, "request")

            # Parse the message
            if message.strip().lower() == "get_data":
                response = self.data_product.get_data()
            elif message.startswith("get_analysis:"):
                analysis_id = message.split(":", 1)[1].strip()
                response = self.data_product.get_analysis(analysis_id)
            elif message.strip().lower() == "get_combined_data":
                response = self.data_product.get_combined_data()
            else:
                response = f"Unknown command: {message}"

            log_data_exchange(self.domain_name, "client", "response")
            return response
        except Exception as e:
            return f"Error: {str(e)}"

    def fetch_data_from_alpha(self) -> bool:
        """Fetch data from the Alpha domain and store it.

        Returns:
            True if successful, False otherwise
        """
        from infra.discovery import get_domain_address

        alpha_address = get_domain_address("domain_alpha")
        if not alpha_address:
            print(f"[{self.domain_name}] Error: Cannot find Alpha domain address")
            return False

        try:
            log_data_exchange(self.domain_name, "domain_alpha", "request")
            host, port = alpha_address
            response = self.client.send_message(host, port, "get_data")

            if response:
                log_data_exchange("domain_alpha", self.domain_name, "response")
                self.data_product.store_alpha_data(response)
                return True
            return False
        except Exception as e:
            print(f"[{self.domain_name}] Error fetching data from Alpha: {e}")
            return False

    def send_message_to_domain(self, target_domain: str, message: str) -> Optional[str]:
        """Send a message to another domain.

        Args:
            target_domain: The name of the domain to send the message to
            message: The message to send

        Returns:
            The response from the target domain, or None if there was an error
        """
        from infra.discovery import get_domain_address

        target_address = get_domain_address(target_domain)
        if not target_address:
            print(f"[{self.domain_name}] Error: Unknown domain '{target_domain}'")
            return None

        try:
            verify_message(message)
            log_data_exchange(self.domain_name, target_domain, "request")
            host, port = target_address
            response = self.client.send_message(host, port, message)
            if response:
                log_data_exchange(target_domain, self.domain_name, "response")
            return response
        except Exception as e:
            print(f"[{self.domain_name}] Error sending message to {target_domain}: {e}")
            return None

    def start_periodic_sync(self, interval_seconds: int = 60) -> None:
        """Start a periodic sync with the Alpha domain.

        Args:
            interval_seconds: The interval between syncs in seconds
        """

        def sync_job():
            while self.sync_running:
                print(f"[{self.domain_name}] Syncing with Alpha domain...")
                self.fetch_data_from_alpha()
                time.sleep(interval_seconds)

        self.sync_running = True
        self.sync_thread = threading.Thread(target=sync_job)
        self.sync_thread.daemon = True
        self.sync_thread.start()
        print(f"[{self.domain_name}] Started periodic sync with Alpha domain (interval: {interval_seconds}s)")