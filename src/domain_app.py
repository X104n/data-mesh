from config import socket_setup
from domain.data_product import DataProduct
from domain.artifact import Artifact
import time
import threading 
import socket
import platform1.gateway as gateway
import json
from TUI.main import choose_from_list

prodoucts = []

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

def get_product(product):
    # Get the product domain
    product_domain = None

    # Contact the domain server to get the product
    full_product = None

    return full_product

def handle_client(domain_server):
    """Handle client connection"""
    while True:
        data = domain_server.recv(1024).decode()
        if not data:
            break
        elif data == "consume":
            print("Received consume request")
            domain_server.sendall(b"ok")
            gateway.server_consume(domain_server, prodoucts)
        break
    
    print(f"Connection with {domain_server.getpeername()[0]} closed")
    domain_server.close()
    
    

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
    '''
    Getting the platform IP
    ===========================
    '''

    platform_ip = "10.0.3.5"

    # Start the domain server
    domain_server = socket_setup()
    threading.Thread(target=start_listening, args=(domain_server,), daemon=True).start()

    '''
    ==========================
    '''

    # Announce presence to the mesh
    domain_client = socket_setup(server=False)
    mesh_hello(domain_client)

    time.sleep(1)

    # Get available domains from platform
    domain_client = socket_setup(server=False)
    domains = get_mesh(domain_client)
    print(f"Domains: {domains}")
    
    time.sleep(1)

    '''
    Create a data product and artifact
    ==========================
    '''

    data_product = _create_product(1)
    prodoucts.append(data_product)
    artifact = _create_artifact(1, data_product=data_product, data={"key1": "value1"})
    data_product.artifacts.append(artifact)
    artifact = _create_artifact(5, data_product=data_product, data={"key5": "value5"})
    data_product.artifacts.append(artifact)
    
    '''
    Make the data product discoverable
    ==========================
    '''

    register_client = socket_setup(server=False)
    gateway.client_discover_registration(data_product, register_client)


    '''
    ==========================
    '''

    # Get product from other domains
    discover_client = socket_setup(server=False)
    mesh_products_json = gateway.client_discover_products(discover_client)
    mesh_products = json.loads(mesh_products_json)
    print(f"Mesh products: {mesh_products}")

    
    # Choose a product from the mesh
    asking_product_nr = choose_from_list("Choose one of the mesh products",mesh_products)
    asking_product = mesh_products[asking_product_nr]
    print(f"Chosen product: {asking_product}")


    
    # Get the product from the domain
    consume_client = socket_setup(server=False)
    product_name = asking_product[0]
    domain = asking_product[1]
    product = gateway.client_consume(product_name, domain, consume_client)
    print(f"Product: {product}")

    with open("src/domain/test.txt", "w") as f:
        f.write(product)

    '''
    ==========================
    '''

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")