import json
import time
import csv
import socket
import threading

# Local imports
from config import socket_setup
from domain import DataProduct, Artifact
from platform_code import gateway

# Global variable
products = []
zero_trust = False

def _create_product(number: int, domain):
    data_product = DataProduct(
        data_id=number,
        name=f"Data Product {number}",
        domain=domain,
        artifacts=[],
    )
    return data_product

def _create_artifact(number: int, data_product=None, data={"key": "value"}):
    return Artifact(
        data_id=number,
        name=f"Artifact {number}",
        data_product=data_product,
        data=data,
    )

def handle_client(domain_server):
    while True:
        request_type = domain_server.recv(1024).decode()
        if not request_type:
            break
        elif request_type == "consume":
            print("Received consume request")
            domain_server.sendall(b"ok")

            auth_client_socket = socket_setup(server=False)
            gateway.server_consume(domain_server, products, auth_client_socket, zero_trust)
            break
        else:
            print(f"Unknown request type: {request_type}")
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
            
            threading.Thread(target=handle_client, args=(conn,), daemon=True).start()
        except socket.timeout:
            continue
        except KeyboardInterrupt:
            print("Server shutting down...")
            break

def time_keeping(start_time, message=None):
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("=====================\n")
    print(f"Elapsed time: {elapsed_time} seconds")
    if message == None:
        print("No product found")
    print("\n=====================")

    with open("src/domain_app.csv", "a", newline='') as f:
        writer = csv.writer(f, delimiter=';')
        if message is None:
            writer.writerow([message])
        else:
            writer.writerow([elapsed_time])

if __name__ == "__main__":
    '''
    Zero Trust, and clear files
    ==========================
    '''
    zero_trust = input("Should the program use zero trust? (y/n): ").strip().lower() == "y"

    with open("src/domain_app.csv", "w") as f:
        writer = csv.writer(f)

    with open("src/platform_code/local_db.json", "w") as f:
        platform_up = '{"platform": {"domain": "10.0.3.5"} }'
        json.dump(json.loads(platform_up), f, indent=4)

    with open("src/platform_code/local_db.json", "r") as f:
        db = json.load(f)
    platform_ip = db["platform"]["domain"]
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
    hello_client = socket_setup(server=False)
    gateway.client_hello(hello_client)
    '''
    Create a data product and artifacts
    ==========================
    '''
    data_product = _create_product(1, domain_ip)
    products.append(data_product)

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

    for i in range(0, 10_000):
        print("Consume product start")

        start_time = time.time()

        # Visit the marketplace to get all the mesh products
        discover_client = socket_setup(server=False)
        mesh_products_json = gateway.client_discover_products(discover_client)
        if mesh_products_json is None:
            time_keeping(start_time, "Mesh products not found")
            time.sleep(1)
            continue
        mesh_products = json.loads(mesh_products_json)
        print(f"Mesh products: {mesh_products}")

        # Remove own product(s)
        choose_products = []
        for product in mesh_products:
            if product[1] != domain_ip:
                choose_products.append(product)

        print(f"Products not including this domains product: {choose_products}")
        
        if len(choose_products) == 0:
            time_keeping(start_time, "No products to consume")
            time.sleep(1)
            continue
        else:
            chosen_product = choose_products[i % len(choose_products)]
            print(f"Chosen product: {chosen_product}")

        # Get the product from the domain
        consume_client = socket_setup(server=False)
        product_name = chosen_product[0]
        domain = chosen_product[1]
        product = gateway.client_consume(product_name, domain, consume_client)
        
        if product is None:
            print("Error in consuming data")
            time_keeping(start_time, "No product found")
            time.sleep(1)
            continue

        elif product == "Authentication rejected":
            print("Authentication rejected")
            time_keeping(start_time, "Authentication rejected")

            hello_client = socket_setup(server=False)
            gateway.client_hello(hello_client)
            continue

        time_keeping(start_time, True)
        print(f"Product: {product}")
    '''
    Make sure the server do not exit
    ==========================
    '''
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")