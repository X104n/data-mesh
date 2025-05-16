import threading
import socket
import json

from config import socket_setup
from platform1 import auther, gateway, logger

zero_trust = False

def start_listening(server):
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
    try:
        while True:
            request_type = conn.recv(1024).decode()

            if not request_type:
                break
            elif request_type == "hello":
                addr = conn.getpeername()[0]

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
                logger.log("Hello", addr)

                conn.sendall(b"ok")

            elif request_type == "get_mesh":
                print("Sending mesh data")
                with open("src/platform1/marketplace.json", "r") as f:
                    marketplace = json.load(f)
                mesh_data = json.dumps(list(marketplace.keys())).encode()
                conn.sendall(mesh_data)

            elif request_type == "discover/registration":
                conn.sendall(b"ok")
                gateway.platform_discover_registration(conn)

            elif request_type == "discover":
                print("Received discover")
                conn.sendall(b"ok")
                gateway.platform_discover_products(conn, zero_trust)

            elif request_type == "authenticate":
                print("Received authentication request")
                conn.sendall(b"ok")
                if not auther.server_authenticate("authenticate", conn, zero_trust):
                    print("Authentication failed")
                    conn.sendall(b"authentication failed")
                else:
                    conn.sendall(b"ok")

            print(f"Received request: {request_type}")
            break
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    zero_trust = input("Do you want to enable zero trust? (y/n): ").strip().lower() == 'y'

    with open("src/platform1/marketplace.json", "w") as f:
        json.dump({}, f, indent=4)
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