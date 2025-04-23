from config import socket_setup
from domain.data_product import DataProduct
from domain.artifact import Artifact
import time
import threading
import socket

platform_ip = "10.0.3.5"

def _create_product(number: int):
    data_product = DataProduct(
        data_id=number,
        name=f"Data Product {number}",
        domain=f"Domain {number}",
        artifacts=[],
    )
    return data_product

def _create_artifact(number: int, data_product=None, data={"key": "value"}):
    artifact = Artifact(
        data_id=number,
        name=f"Artifact {number}",
        data_product=data_product,
        data=data,
    )
    return artifact

def mesh_hello(domain_client):
    while True:
        domain_client.connect((platform_ip, 9000))
        domain_client.sendall(b"hello")
        data = domain_client.recv(1024)
        if data == b"ok":
            print("Announced presence to the mesh")
        break

def get_mesh(domain_client):
    domain_client.connect((platform_ip, 9000))
    domain_client.sendall(b"get_mesh")
    data = domain_client.recv(1024)
    if data:
        return data.decode()
    else:
        print("No data received from the mesh")

def get_product(domain):
    domain_client = socket_setup(server=False)
    domain_client.connect((domain, 9000))
    domain_client.sendall(b"get_product")
    data = domain_client.recv(1024).decode()
    if data:
        return data
    else:
        print("No data received from the product")

def handle_client(domain_server):
    print("Testing")
    

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

if __name__ == "__main__":

    # Start the domain server
    domain_server = socket_setup()
    threading.Thread(target=start_listening, args=(domain_server,), daemon=True).start()

    # Announce presence to the mesh
    domain_client = socket_setup(server=False)
    mesh_hello(domain_client)

    time.sleep(1)

    # Get available domains from platform
    domain_client = socket_setup(server=False)
    domains = get_mesh(domain_client)
    print(f"Domains: {domains}")
    
    time.sleep(1)

    # Create a product and artifact
    data_product = _create_product(1)
    artifact = _create_artifact(1, data_product=data_product)

    # Get product from other domains

    #product = get_product(domains)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")