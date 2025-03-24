import os
import pytest
import socket
import sys
from unittest.mock import patch, MagicMock

# Direct import of the modules
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from src import producer
from src import consumer


class TestProducer:
    @patch('socket.socket')
    @patch('os.listdir')
    def test_producer_initialization(self, mock_listdir, mock_socket):
        """Test that the producer initializes correctly"""
        # Mock the socket behavior
        mock_server_socket = MagicMock()
        mock_socket.return_value = mock_server_socket

        # Mock os.listdir to return fake weather files
        mock_listdir.return_value = ['weather_data_1.csv', 'weather_data_2.csv']

        # Mock socket.accept to return after one connection
        mock_client_socket = MagicMock()
        mock_client_socket.recv.return_value = b'1'
        mock_server_socket.accept.return_value = (mock_client_socket, ('127.0.0.1', 12345))

        # Interrupt the infinite loop after one iteration
        def side_effect(*args, **kwargs):
            # Raise exception to break out of the infinite loop
            raise StopIteration("Breaking out of the loop")

        mock_server_socket.accept.side_effect = side_effect

        # Mock open to avoid file access
        with patch('builtins.open', MagicMock()):
            # Call producer code but catch the StopIteration to exit the loop
            with patch('builtins.print'):  # Suppress print statements
                try:
                    producer.start_server()
                except StopIteration:
                    pass

        # Verify socket was initialized correctly
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_server_socket.bind.assert_called_once_with(('', 9999))
        mock_server_socket.listen.assert_called_once_with(5)


class TestConsumer:
    @patch('socket.socket')
    @patch('builtins.input')
    def test_consumer_initialization(self, mock_input, mock_socket):
        """Test that the consumer initializes correctly"""
        # Mock the socket behavior
        mock_client_socket = MagicMock()
        mock_socket.return_value = mock_client_socket

        # Mock user input
        mock_input.return_value = '1'

        # Mock socket.recv to return data once then empty
        mock_client_socket.recv.side_effect = [b'Welcome message', b'file content', b'']

        # Mock open to avoid file access
        mock_file = MagicMock()
        mock_open = MagicMock(return_value=mock_file)

        with patch('builtins.open', mock_open):
            # Call start_client with suppressed prints
            with patch('builtins.print'):
                consumer.start_client()

        # Verify socket was initialized correctly
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_client_socket.connect.assert_called_once_with(('192.168.168.42', 9999))
        mock_client_socket.send.assert_called_once_with(b'1')