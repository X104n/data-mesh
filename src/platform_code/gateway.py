import json

# Local imports
from .authenticate import client_authenticate
from .logger import log
from config import IP_ADDRESSES

def _log_helper(message, socket):
    addr = socket.getpeername()[0]
    log(message, addr)

def _get_platform_ip():
    with open("src/platform_code/marketplace.json", "r") as f:
        marketplace = json.load(f)
    return marketplace["platform"]["domain"]

'''
Functions used by the domains
=========================
'''
def client_hello(socket_connectin):
        platform_ip = _get_platform_ip()
        socket_connectin.connect((platform_ip, 9000))

        socket_connectin.sendall(b"hello")
        response = socket_connectin.recv(1024).decode()

        if response == "ok":
            hello_success = socket_connectin.recv(1024)
            if hello_success == b"ok":
                return True
        return False
        
def client_discover_products(socket_connection):
    try:
        platform_ip = _get_platform_ip()
        socket_connection.connect((platform_ip, 9000))

        socket_connection.sendall(b"discover")
        response = socket_connection.recv(1024).decode()
        
        if response == "ok":
            products = socket_connection.recv(1024).decode()
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
        socket_connection.close()
    
def client_discover_registration(data_product, socket_connection):
    try:
        platform_ip = _get_platform_ip()
        socket_connection.connect((platform_ip, 9000))

        socket_connection.sendall(b"discover/registration")
        response = socket_connection.recv(1024).decode()

        if response == "ok":
            socket_connection.sendall(data_product.name.encode())

            response = socket_connection.recv(1024).decode()
            if response == "ok":
                return
    except Exception as e:
        print(f"Error in client discover registration: {e}")
    finally:
        socket_connection.close()

def client_consume(product_name, product_domain, socket_connection):
    try:
        socket_connection.connect((product_domain, 9000))
        socket_connection.sendall(b"consume")
        
        response = socket_connection.recv(1024).decode()
        if response == "ok":
            authenticated = socket_connection.recv(1024).decode()
            
            if authenticated == "ok":
                socket_connection.sendall(product_name.encode())
                requested_product = socket_connection.recv(1024).decode()
                return requested_product
            
            elif authenticated == "Authentication rejected":
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
        socket_connection.close()
    
def server_consume(domain_socket_connectin, products, platform_socket_connection, zero_trust):
    addr = domain_socket_connectin.getpeername()[0]

    if zero_trust:
        if not client_authenticate("consume", addr, platform_socket_connection):
            domain_socket_connectin.sendall(b"Authentication rejected")
            return
        domain_socket_connectin.sendall(b"ok")
    else:
        valid_ips = IP_ADDRESSES
        if addr in valid_ips:
            domain_socket_connectin.sendall(b"ok")
        else:
            domain_socket_connectin.sendall(b"error")
            return

    dataproduct_request = domain_socket_connectin.recv(1024).decode()
    
    for product in products:
        if product.name == dataproduct_request:
            product_dict = product.to_dict()
            json_str = json.dumps(product_dict)
            domain_socket_connectin.sendall(json_str.encode())
            break
    else:
        domain_socket_connectin.sendall(b"error")

'''
Functions used by the platform
=========================
'''

def server_hello(socket_connection, zero_trust):
    if zero_trust:
        _log_helper("Hello", socket_connection)

    with open("src/platform_code/marketplace.json", "r") as f:
        marketplace = json.load(f)

    addr = socket_connection.getpeername()[0]
    if addr not in marketplace:
        marketplace[addr] = {
            "domain": addr,
            "products": []
        }
        with open("src/platform_code/marketplace.json", "w") as f:
            json.dump(marketplace, f, indent=4)
    socket_connection.sendall(b"ok")

def server_discover_products(socket_connection, zero_trust):
    if zero_trust:
        _log_helper("Discovering products", socket_connection)

    with open("src/platform_code/marketplace.json", "r") as f:
        marketplace = json.load(f)

    product_domain_pairs = []
    for domain in marketplace:
        if domain != "platform":
            for product in marketplace[domain]["products"]:
                product_domain_pairs.append([product, domain])
    json_data = json.dumps(product_domain_pairs).encode()
    socket_connection.sendall(json_data)
            
def platform_discover_registration(socket_connection, zero_trust):
    if zero_trust:
        _log_helper("Discovering registration", socket_connection)

    with open("src/platform_code/marketplace.json", "r") as f:
        marketplace = json.load(f)

    data_product_name = socket_connection.recv(1024).decode()
    addr = socket_connection.getpeername()[0]
    if addr in marketplace:
        if data_product_name not in marketplace[addr]["products"]:
            marketplace[addr]["products"].append(data_product_name)
        with open("src/platform_code/marketplace.json", "w") as f:
            json.dump(marketplace, f, indent=4)
        socket_connection.sendall(b"ok")
    else:
        socket_connection.sendall(b"error")
