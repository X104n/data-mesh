from config import socket_setup
import threading
import socket

domains = []

def start_listening(server):
    """Start listening, and create new thread for each connection"""
    server.settimeout(1)
    while True:
        try:
            conn, addr = server.accept()
            print(f"Connection from {addr} has been established!")
            
            threading.Thread(target=handle_client, args=(conn,)).start()
        except socket.timeout:
            continue
        except KeyboardInterrupt:
            print("Server shutting down...")
            break

def handle_client(conn):
    """Handle client connection"""
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        
        if data == "hello":
            addr = conn.getpeername()[0]
            print(f"Received hello from {addr}")
            domains.append(addr)
            conn.sendall(b"ok")

        if data == "get_mesh":
            print("Sending mesh data")
            mesh_data = domains.encode()
            conn.sendall(mesh_data)

    conn.close()
    print("Connection closed")

if __name__ == "__main__":
    server = socket_setup()

    start_listening(server)