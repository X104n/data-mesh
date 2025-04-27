from config import socket_setup
from domain.data_product import DataProduct
from domain.artifact import Artifact
import time
import threading 
import socket
import platform1.gateway as gateway
import json
from TUI.main import choose_from_list
import csv

prodoucts = []

def _create_product(number: int, domain):
    data_product = DataProduct(
        data_id=number,
        name=f"Data Product {number}",
        domain=domain,
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
            auth_client_socket = socket_setup(server=False)
            gateway.server_consume(domain_server, prodoucts, auth_client_socket)
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

def time_keeping(start_time, product_found):
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("=====================\n")
    print(f"Elapsed time: {elapsed_time} seconds")
    if not product_found:
        print("No product found")
    print("\n=====================")

    # Write the elapsed_time to a CSV file
    with open("src/domain_app.csv", "a", newline='') as f:
        writer = csv.writer(f)
        if not product_found:
            writer.writerow(["No product found"])
        writer.writerow([elapsed_time])  # Pass values as a list
        times.append(elapsed_time)

if __name__ == "__main__":

    times = []

    '''
    Set the platform IP address
    ===========================
    '''

    with open("src/platform1/marketplace.json", "w") as f:
        platform_up = '{"platform": {"domain": "10.0.3.5"} }'
        json.dump(json.loads(platform_up), f, indent=4)

    platform_ip = "10.0.3.5"

    '''
    Starting the domain server socket
    ==========================
    '''

    domain_server = socket_setup()
    threading.Thread(target=start_listening, args=(domain_server,), daemon=True).start()

    domain_ip = domain_server.getsockname()[0]
    print(f"Domain server started at {domain_ip}")
    
    '''
    Announce presence to the platform
    ==========================
    '''

    domain_client = socket_setup(server=False)
    mesh_hello(domain_client)

    #domain_client = socket_setup(server=False)
    #domains = get_mesh(domain_client)
    #print(f"Domains: {domains}")

    '''
    Create a data product and artifacts
    ==========================
    '''

    data_product = _create_product(1, domain_ip)
    prodoucts.append(data_product)

    artifact = _create_artifact(1, data_product=data_product, data={"key1": "value1"})
    data_product.artifacts.append(artifact)
    
    '''
    Make the data product discoverable
    ==========================
    '''

    register_client = socket_setup(server=False)
    gateway.client_discover_registration(data_product, register_client)

    '''
    Choose products from the mesh on repeat
    ==========================
    '''

    input("Press Enter to start consuming products from the mesh...")

    while True:
        start_time = time.time()

        print("Consume product start")

        # Visit the marketplace to get all the mesh products
        discover_client = socket_setup(server=False)
        mesh_products_json = gateway.client_discover_products(discover_client)
        if mesh_products_json is None:
            print("No mesh products found")
            time_keeping(start_time, False)
            time.sleep(5)
            continue
        mesh_products = json.loads(mesh_products_json)
        print(f"Mesh products: {mesh_products}")

        # Remove own product(s)
        choose_products = []
        for product in mesh_products:
            if product[1] != domain_ip:
                choose_products.append(product)

        print(f"Products not including this domains product: {choose_products}")
        
        chosen_product = choose_products[0]
        print(f"Chosen product: {chosen_product}")

        # Get the product from the domain
        consume_client = socket_setup(server=False)
        product_name = chosen_product[0]
        domain = chosen_product[1]
        product = gateway.client_consume(product_name, domain, consume_client)
        print(f"Product: {product}")

        time_keeping(start_time, True)
        
    '''
    Make sure the server do not exit
    ==========================
    '''

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")