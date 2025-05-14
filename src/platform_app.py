import threading
import socket
import json

# Local imports
from config import socket_setup
from platform1 import auther, gateway, logger

zero_trust = False

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
        
        # Hello request
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
        
        # Get mesh request
            elif data == "get_mesh":
                print("Sending mesh data")
                with open("src/platform1/marketplace.json", "r") as f:
                    marketplace = json.load(f)
                mesh_data = json.dumps(list(marketplace.keys())).encode()
                conn.sendall(mesh_data)

        # Registration request
            elif data == "discover/registration":
                print("Received discover/registration")
                conn.sendall(b"ok")
                gateway.platform_discover_registration(conn)

        # Discover request
            elif data == "discover":
                print("Received discover")
                conn.sendall(b"ok")
                gateway.platform_discover_products(conn, zero_trust)

        # Authenticate request
            elif data == "authenticate":
                print("Received authentication request")
                print(f"The data is: {data}")
                conn.sendall(b"ok")
                if not auther.server_authenticate(data, conn):
                    print("Authentication failed")
                    break
                conn.sendall(b"ok")

            break
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    zero_trust = input("Do you want to enable zero trust? (y/n): ").strip().lower() == 'y'
    
    # Clear json file from previous session
    with open("src/platform1/marketplace.json", "w") as f:
        json.dump({}, f, indent=4)

    # Clear log file
    logger.reset_log_file()

    server = socket_setup()

    '''
    Wrinting the platforms ip to the marketplace
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
    Starting the platform server socket
    ====================
    '''
    start_listening(server)