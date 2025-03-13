import socket


def start_client():
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get local machine name
    host = socket.gethostname()
    port = 9999

    # Connection to server
    print(f"Attempting to connect to {host}:{port}...")
    client_socket.connect((host, port))

    # Receive welcome message from server
    welcome_msg = client_socket.recv(1024).decode('utf-8')
    print(f"Server says: {welcome_msg}")

    # Send a message to server
    message = "Hello from the client!"
    client_socket.send(message.encode('utf-8'))

    # Receive response from server
    response = client_socket.recv(1024).decode('utf-8')
    print(f"Server says: {response}")

    # Close the connection
    client_socket.close()
    print("Connection closed")


if __name__ == "__main__":
    start_client()