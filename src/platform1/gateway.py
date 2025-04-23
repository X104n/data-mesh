import json

def client_discover_products(socket):

    # Get platform ip from json file
    with open("src/platform1/marketplace.json", "r") as f:
        marketplace = json.load(f)
    platform_ip = marketplace["platform"]["domain"]

    socket.connect((platform_ip, 9000))
    socket.sendall(b"discover")
    connection = socket.recv(1024).decode()
    if connection == "ok":
        products = socket.recv(1024).decode()
        return products
    else:
        print("Error in discovering products")
        return None

def platform_discover_products(domain_server):

    # TODO Authenticate the user
    addr = domain_server.getpeername()
    # authenticate("discover", addr)

    with open("src/platform1/marketplace.json", "r") as f:
        marketplace = json.load(f)
    
    # Create a list with product-domain pairs
    product_domain_pairs = []
    for domain in marketplace:
        if domain != "platform":
            for product in marketplace[domain]["products"]:
                product_domain_pairs.append([product, domain])
    
    # Convert to JSON and send
    json_data = json.dumps(product_domain_pairs).encode()
    domain_server.sendall(json_data)

    

    

def client_discover_registration(data_product, socket):
    
    # Get platform ip from json file
    with open("src/platform1/marketplace.json", "r") as f:
        marketplace = json.load(f)
    platform_ip = marketplace["platform"]["domain"]

    socket.connect((platform_ip, 9000))
    socket.sendall(b"discover/registration")
    connection = socket.recv(1024).decode()
    
    if connection == "ok":
        socket.sendall(data_product.name.encode())
        response = socket.recv(1024).decode()
        if response == "ok":
            print(f"Data product {data_product.name} registered successfully")
            
def platform_discover_registration(domain_server):
    addr = domain_server.getpeername()

    data_product_name = domain_server.recv(1024).decode()

    with open("src/platform1/marketplace.json", "r") as f:
        marketplace = json.load(f)
    
    if addr[0] in marketplace:
        
        if data_product_name not in marketplace[addr[0]]["products"]:
            marketplace[addr[0]]["products"].append(data_product_name)

        with open("src/platform1/marketplace.json", "w") as f:
            json.dump(marketplace, f, indent=4)
        
        domain_server.sendall(b"ok")
    else:
        domain_server.sendall(b"error")


def client_consume(product_name, product_domain, client_socket):
    
    client_socket.connect((product_domain, 9000))
    client_socket.sendall(b"consume")
    connection = client_socket.recv(1024).decode()
    if connection == "ok":
        client_socket.sendall(product_name.encode())
        data = client_socket.recv(1024).decode()
        return data
    else:
        print("Error in consuming data")
        return None

def server_consume(server_socket, products):
    # TODO Authenticate the user
    addr = server_socket.getpeername()
    # authenticate("consume", addr)

    # Get the product name from the client
    data = server_socket.recv(1024).decode()
    
    # Find the corelating data product from the products list
    for product in products:
        if product.name == data:
            # Convert dictionary to JSON string first, then encode to bytes
            product_dict = product.to_dict()
            json_str = json.dumps(product_dict)
            server_socket.sendall(json_str.encode())
            break
    else:
        server_socket.sendall(b"error")