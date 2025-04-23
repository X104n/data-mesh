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
    '''
    Give the list of all available products in the mesh without disclosing the ip address of the domain.
    '''

    # Authenticate the user
    addr = domain_server.getpeername()
    # authenticate("discover", addr)


    with open("src/platform1/marketplace.json", "r") as f:
        marketplace = json.load(f)
    
    # Get a list of only the products in the marketplace
    products = []
    for domain in marketplace:
        if domain != "platform":
            products.extend(marketplace[domain]["products"])

    products = json.dumps(products).encode()
    domain_server.sendall(products)

    

    

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


def consume(client_socket,):
    """Consume data from the mesh"""
    # Connect to the mesh and consume data
    print("Consuming data from the mesh...")
    pass