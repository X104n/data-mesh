import socket

def start_server():
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get local machine name
    host = ''
    port = 9999

    # Bind to the port
    server_socket.bind((host, port))

    # Queue up to 5 requests
    server_socket.listen(5)

    print(f"Server started on {host}:{port}")
    print("Waiting for client connection...")

    while True:
        # Establish connection with client
        client_socket, addr = server_socket.accept()
        print(f"Got a connection from {addr}")

        # Sending data
        data = "This is the data that you requested"
        client_socket.send(data.encode('utf-8'))

        # Receive data from client
        data = client_socket.recv(1024).decode('utf-8')
        print(f"Client says: {data}")

        # Send a response
        response = f"I received your message: '{data}'"
        client_socket.send(response.encode('utf-8'))

        # Close the connection
        client_socket.close()
        print("Connection closed")


if __name__ == "__main__":
    start_server()