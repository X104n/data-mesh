import json
from .logger import log

def client_authenticate(action, addr_to_check, domain_client_socket):
    try:
        with open("src/platform_code/marketplace.json", "r") as f:
            marketplace = json.load(f)
        platform_ip = marketplace["platform"]["domain"]
        
        domain_client_socket.connect((platform_ip, 9000))
        domain_client_socket.sendall("authenticate".encode())

        request_received = domain_client_socket.recv(1024).decode()
        
        if request_received == "ok":
            auth_msg = f"{action}/{addr_to_check}"
            domain_client_socket.sendall(auth_msg.encode())
            
            auth_response = domain_client_socket.recv(1024).decode()
            if auth_response == "ok":
                return True
            else:
                print(f"Authentication failed for action: {action} - response: {auth_response}")
                return False
        else:
            print(f"Error in authentication process - response: {request_received}")
            return False
    except Exception as e:
        print(f"Exception during authentication: {e}")
        return False
    finally:
        domain_client_socket.close()

def server_authenticate(platform_server_socket, zero_trust):
    authentication_request = platform_server_socket.recv(1024).decode()
    if not authentication_request:
        platform_server_socket.sendall(b"error")
        return

    action, addr_to_check = authentication_request.split("/")
    valid_address = False

    if zero_trust:
        valid_address = True
    else:
        valid_address = True
    
    if valid_address:
        if action == "discover":
            log("Authentication accept to discover request", addr_to_check)
            platform_server_socket.sendall(b"ok")
            return
        elif action == "consume":
            log("Authentication accept to consume request", addr_to_check)
            platform_server_socket.sendall(b"ok")
            return
        else:
            log("Authentication error", addr_to_check)
            platform_server_socket.sendall(b"error")
            return
    else:
        log("Authentication reject", addr_to_check)
        platform_server_socket.sendall(b"error")
        return