"""
Socket Manager module for the data mesh demo.
Provides abstractions for socket operations used by domain controllers.
"""

import socket
import threading
import time
from typing import Tuple, Callable, Optional, Dict, Any


class SocketServer:
    """A simple socket server that listens for incoming connections."""

    def __init__(self, host: str, port: int, domain_name: str):
        """Initialize the socket server.

        Args:
            host: The host to bind to
            port: The port to bind to
            domain_name: The name of the domain this server belongs to
        """
        self.host = host
        self.port = port
        self.domain_name = domain_name
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = False
        self.handler = None
        self.thread = None

    def set_message_handler(self, handler: Callable[[str, Tuple[str, int]], None]) -> None:
        """Set the handler function for incoming messages.

        Args:
            handler: A function that takes a message string and client address tuple
        """
        self.handler = handler

    def start(self) -> None:
        """Start the server in a separate thread."""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        self.thread = threading.Thread(target=self._run_server)
        self.thread.daemon = True
        self.thread.start()
        print(f"[{self.domain_name}] Server started on {self.host}:{self.port}")

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
            if data and self.handler:
                response = self.handler(data, client_address)
                if response:
                    client_socket.send(response.encode('utf-8'))
        except Exception as e:
            print(f"[{self.domain_name}] Error handling client: {e}")
        finally:
            client_socket.close()

    def stop(self) -> None:
        """Stop the server."""
        self.running = False
        if hasattr(self, 'server_socket'):
            self.server_socket.close()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        print(f"[{self.domain_name}] Server stopped")


class SocketClient:
    """A simple socket client that can connect to a server and send messages."""

    def __init__(self, domain_name: str):
        """Initialize the socket client.

        Args:
            domain_name: The name of the domain this client belongs to
        """
        self.domain_name = domain_name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_message(self, host: str, port: int, message: str) -> Optional[str]:
        """Send a message to a server and return the response.

        Args:
            host: The host to connect to
            port: The port to connect to
            message: The message to send

        Returns:
            The server's response as a string, or None if there was an error
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.socket.send(message.encode('utf-8'))

            # Wait for response with a timeout
            self.socket.settimeout(5)
            response = self.socket.recv(1024).decode('utf-8')
            print(f"[{self.domain_name}] Sent: '{message}', Received: '{response}'")
            return response
        except Exception as e:
            print(f"[{self.domain_name}] Error sending message: {e}")
            return None
        finally:
            self.socket.close()