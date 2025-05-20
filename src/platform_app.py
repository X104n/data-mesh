import threading
import socket
import json

from config import socket_setup
from platform_code import authenticate, gateway, logger

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
            log_file.close()
            break

def handle_client(socket_connection):
    try:
        while True:
            request_type = socket_connection.recv(1024).decode()

            if not request_type:
                break
            elif request_type == "hello":
                socket_connection.sendall(b"ok")
                gateway.server_hello(socket_connection)

            elif request_type == "discover/registration":
                socket_connection.sendall(b"ok")
                gateway.platform_discover_registration(socket_connection)

            elif request_type == "discover":
                socket_connection.sendall(b"ok")
                gateway.server_discover_products(socket_connection, zero_trust)

            elif request_type == "authenticate":
                socket_connection.sendall(b"ok")

                authentication_response = authenticate.server_authenticate(socket_connection, zero_trust, log_file)
                print(f"Authentication response: {authentication_response}")
                if authentication_response == "Accepted":
                    socket_connection.sendall(b"ok")
                elif authentication_response == "Rejected":
                    socket_connection.sendall(b"authentication rejected")
                else:
                    socket_connection.sendall(b"error")
            break
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        socket_connection.close()

if __name__ == "__main__":
    zero_trust = input("Do you want to enable zero trust? (y/n): ").strip().lower() == 'y'

    with open("src/platform_code/marketplace.json", "w") as f:
        json.dump({}, f, indent=4)
    logger.reset_log_file()

    server = socket_setup()

    log_file = open("src/platform_code/log.csv", "a+b")
    '''
    Writing the platforms ip to the marketplace
    ====================
    '''
    host = server.getsockname()[0]
    with open("src/platform_code/marketplace.json", "r") as f:
        marketplace = json.load(f)
    if "platform" not in marketplace:
        marketplace["platform"] = {
            "domain": host,
            "products": []
        }
        with open("src/platform_code/marketplace.json", "w") as f:
            json.dump(marketplace, f, indent=4)
    print(f"Host and port {host}:{server.getsockname()[1]}")
    '''
    Starting the platform server socket
    ====================
    '''
    start_listening(server)