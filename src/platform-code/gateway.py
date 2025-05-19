import json

# Local imports
from .auther import client_authenticate
from .logger import log
from config import IP_ADDRESSES

def log_helper(message, socket):
    addr = socket.getpeername()[0]
    log(message, addr)

'''
Functions used by the domains
=========================
'''
def client_hello(domain_client):
        with open("src/platform-code/marketplace.json", "r") as f:
            marketplace = json.load(f)
        platform_ip = marketplace["platform"]["domain"]

        domain_client.connect((platform_ip, 9000))
        domain_client.sendall(b"hello")
        data = domain_client.recv(1024)
        if data == b"ok":
            return True
        return False
        
def client_discover_products(socket):
    """Used by a client socket to discover products from the marketplace"""
    try:
        # Get platform ip from the JSON file
        with open("src/platform-code/marketplace.json", "r") as f:
            marketplace = json.load(f)
        platform_ip = marketplace["platform"]["domain"]

        # Connect to the platform and get the mesh products
        socket.connect((platform_ip, 9000))
        socket.sendall(b"discover")
        response = socket.recv(1024).decode()
        
        if response == "ok":
            products = socket.recv(1024).decode()
            return products
        elif response.startswith("ok"):
            products = response[2:]  # Remove the "ok" part
            return products
        else:
            print("Error in discovering products:", response)
            return None
    except Exception as e:
        print(f"Error in client discover products: {e}")
        return None
    finally:
        socket.close()
    
def client_discover_registration(data_product, socket):
    try:
        # Get platform ip from the JSON file
        with open("src/platform-code/marketplace.json", "r") as f:
            marketplace = json.load(f)
        platform_ip = marketplace["platform"]["domain"]

        # Connect to the platform and register the data product in the marketplace
        socket.connect((platform_ip, 9000))
        socket.sendall(b"discover/registration")
        connection = socket.recv(1024).decode()
        if connection == "ok":
            socket.sendall(data_product.name.encode())
            response = socket.recv(1024).decode()
            if response == "ok":
                print(f"Data product {data_product.name} registered successfully")
    except Exception as e:
        print(f"Error in client discover registration: {e}")
    finally:
        socket.close()

def client_consume(product_name, product_domain, client_socket):
    try:
        client_socket.connect((product_domain, 9000))
        client_socket.sendall(b"consume")
        
        request_received = client_socket.recv(1024).decode()
        if request_received == "ok":
            print(f"Received request to consume {product_name} from {product_domain}")
            authenticated = client_socket.recv(1024).decode()
            
            if authenticated == "ok":
                print(f"Authenticated for consumption of {product_name}")
                client_socket.sendall(product_name.encode())
                requested_product = client_socket.recv(1024).decode()
                return requested_product
            
            elif authenticated == "Authentication failed":
                return authenticated
            
            else:
                print(f"Error in authentication - Auth response: {authenticated}")
                return None
        
        else:
            print("Error in consuming data")
            return None
    except ConnectionResetError:
        print("Connection reset by peer")
        return None
    except Exception as e:
        print(f"Error in client consume: {e}")
        return None
    finally:
        client_socket.close()
    
def server_consume(server_socket, products, client_socket, zero_trust):

    if zero_trust:
        addr = server_socket.getpeername()[0]
        if not client_authenticate("consume", addr, client_socket):
            server_socket.sendall(b"Authentication failed")
            return
        print(f"Address {addr} is eligible for consumption zt")
        server_socket.sendall(b"ok")
    else:
        valid_ips = IP_ADDRESSES
        addr = server_socket.getpeername()[0]
        if addr in valid_ips:
            print(f"Address {addr} is eligible for consumption")
            server_socket.sendall(b"ok")
        else:
            print(f"Address {addr} REJECTED - not in IP_ADDRESSES list")
            server_socket.sendall(b"error")
            return

    dataproduct_request = server_socket.recv(1024).decode()
    
    for product in products:
        if product.name == dataproduct_request:
            product_dict = product.to_dict()
            json_str = json.dumps(product_dict)
            server_socket.sendall(json_str.encode())
            break
    else:
        server_socket.sendall(b"error")

'''
Functions used by the platform
=========================
'''

def platform_discover_products(domain_server, zero_trust):
    if zero_trust:
        log_helper("Discovering products", domain_server)

    # Get the mesh products from the marketplace JSON file
    with open("src/platform-code/marketplace.json", "r") as f:
        marketplace = json.load(f)
    
    # Create a list with (product, domain) pairs
    product_domain_pairs = []
    for domain in marketplace:
        if domain != "platform":
            for product in marketplace[domain]["products"]:
                product_domain_pairs.append([product, domain])
    
    # Convert to JSON and send
    json_data = json.dumps(product_domain_pairs).encode()
    domain_server.sendall(json_data)
            
def platform_discover_registration(domain_server):
    log_helper("Discovering registration", domain_server)

    # Get the address / ip of the domain server.
    addr = domain_server.getpeername()[0]

    # Get the data product name from the client
    data_product_name = domain_server.recv(1024).decode()

    # Adding the product to the marketplace and the domain if it doesn't exist
    with open("src/platform-code/marketplace.json", "r") as f:
        marketplace = json.load(f)
    if addr in marketplace:
        if data_product_name not in marketplace[addr]["products"]:
            marketplace[addr]["products"].append(data_product_name)
        with open("src/platform-code/marketplace.json", "w") as f:
            json.dump(marketplace, f, indent=4)
        domain_server.sendall(b"ok")
    else:
        domain_server.sendall(b"error")
