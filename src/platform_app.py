from config import socket_setup
import threading

def start_listening(server):
    """Start listening, and create new thread for each connection"""
    while True:
        conn, addr = server.accept()
        print(f"Connection from {addr} has been established!")
        
        threading.Thread(target=handle_client, args=(conn,)).start()

def handle_client(conn):
    """Handle client connection"""
    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(f"Received data: {data.decode()}")
        conn.sendall(b"ok")  # Echo back the received data

    conn.close()
    print("Connection closed")

if __name__ == "__main__":
    server = socket_setup()

    start_listening(server)