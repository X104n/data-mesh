from config import socket_setup
import platform1.gateway as gateway
import platform1.auther as auther
import threading
import socket
import json

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
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break

            elif data == "hello":
                addr = conn.getpeername()[0]
                print(f"Received hello from {addr}")

                # Add domain to json file.
                with open("src/platform1/marketplace.json", "r") as f:
                    marketplace = json.load(f)

                if addr not in marketplace:
                    marketplace[addr] = {
                        "domain": addr,
                        "products": []
                    }
                    with open("src/platform1/marketplace.json", "w") as f:
                        json.dump(marketplace, f, indent=4)

                conn.sendall(b"ok")

            elif data == "get_mesh":
                print("Sending mesh data")
                with open("src/platform1/marketplace.json", "r") as f:
                    marketplace = json.load(f)
                "Send only keys of the json file"
                mesh_data = json.dumps(list(marketplace.keys())).encode()
                conn.sendall(mesh_data)

            elif data == "discover/registration":
                print("Received discover/registration")
                conn.sendall(b"ok")
                gateway.platform_discover_registration(conn)

            elif data == "discover":
                print("Received discover")
                conn.sendall(b"ok")
                gateway.platform_discover_products(conn)

            elif data == "authenticate":
                print("Received authentication request")
                conn.sendall(b"ok")
                if not auther.server_authenticate(conn):
                    print("Authentication failed")
                    conn.sendall(b"error")
                    break
                conn.sendall(b"ok")

            break
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Clear json file
    with open("src/platform1/marketplace.json", "w") as f:
        json.dump({}, f, indent=4)

    server = socket_setup()

    '''
    Getting the server ip address
    ====================
    '''

    host = server.getsockname()[0]
    with open("src/platform1/marketplace.json", "r") as f:
        marketplace = json.load(f)
    if "platform" not in marketplace:
        marketplace["platform"] = {
            "domain": host,
            "products": []
        }
        with open("src/platform1/marketplace.json", "w") as f:
            json.dump(marketplace, f, indent=4)
    print(f"Host and port {host}:{server.getsockname()[1]}")
    '''
    ====================
    '''
    start_listening(server)