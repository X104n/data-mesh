"""
Controller module for the Alpha domain.
Handles network communication and business logic.
"""

from typing import Tuple, Optional
import infra
import json

from domain_alpha.data_product import AlphaDataProduct
from infra.socket_manager import SocketServer, SocketClient
from infra.governance import verify_message, log_data_exchange


class AlphaController:
    """Controller for the Alpha domain."""

    def __init__(self, host: str, port: int):
        """Initialize the Alpha controller.

        Args:
            host: The host to bind the server to
            port: The port to bind the server to
        """
        self.domain_name = "domain_alpha"
        self.host = host
        self.port = port
        self.data_product = AlphaDataProduct()
        self.server = SocketServer(host, port, self.domain_name)
        self.client = SocketClient(self.domain_name)

        # Set up message handling
        self.server.set_message_handler(self.handle_message)

    def start(self) -> None:
        """Start the Alpha domain server."""
        self.server.start()
        print(f"[{self.domain_name}] Controller started")

    def stop(self) -> None:
        """Stop the Alpha domain server."""
        self.server.stop()
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

            # Parse the message - expecting a simple command
            # In a real-world scenario, this would be more sophisticated
            if message.strip().lower() == "get_data":
                response = self.data_product.get_data()
            elif message.startswith("get_item:"):
                item_id = message.split(":", 1)[1].strip()
                response = self.data_product.get_item(item_id)
            else:
                response = f"Unknown command: {message}"

            log_data_exchange(self.domain_name, "client", "response")
            return response
        except Exception as e:
            return f"Error: {str(e)}"

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