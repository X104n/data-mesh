import socket


def start_client():
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get local machine name
    host = '192.168.168.42'
    port = 9999

    # Connection to server
    print(f"Attempting to connect to {host}:{port}...")
    client_socket.connect((host, port))

    # Message from server asking what file you want
    query = client_socket.recv(1024).decode('utf-8')
    print(query)

    #Choosing what file you want
    number = input('Choose what number file you wish to acess: ')
    client_socket.send(number.encode('utf-8'))


    # Open a file to receive the data
    with open (f'src/data/received_file_{number}.txt', 'wb') as file:
        # Receive data in chunks
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            file.write(data)

    # Close the connection
    client_socket.close()
    print("Connection closed")


if __name__ == "__main__":
    start_client()