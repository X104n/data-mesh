import socket
import os

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

    weather_files = [f for f in os.listdir('data') if f.startswith('weather_data_') and f.endswith('.csv')]

    print(f"Server started on {host}:{port}")
    print("Waiting for client connection...")

    while True:
        # Establish connection with client
        client_socket, addr = server_socket.accept()
        print(f"Got a connection from {addr}")

        # Asking what file to send
        message = 'Here is the tables I have: (Choose one)\n'
        for file in weather_files:
            message += f"\n{file}"
        client_socket.send(message.encode('utf-8'))


        # Waiting for a response
        file_number = client_socket.recv(1024).decode('utf-8')
        print(f"Client says it want the file number: {file_number}")

        with open(f"data/weather_data_{file_number}.csv", 'rb') as file:
            client_socket.send(file.read())

        # Close the connection
        client_socket.close()
        print("Connection closed")


if __name__ == "__main__":
    start_server()