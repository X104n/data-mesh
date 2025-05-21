import json
import time
from .logger import log

def _read_last_n_lines(f, n):
    f.seek(0, 2)
    size = f.tell()
    if size == 0:
        return []

    position = size - 1
    newlines_found = 0

    while position >= 0:
        f.seek(position)
        char = f.read(1)
        if char.decode() == '\n':
            newlines_found += 1
            if newlines_found == n and position > 0:
                position += 1
                break
        position -= 1

    if position < 0:
        position = 0

    f.seek(position)
    last_chunk = f.read().decode()
    last_lines = last_chunk.splitlines()

    return last_lines

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
            elif auth_response == "authentication rejected":
                return False
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

def server_authenticate(platform_server_socket, zero_trust, log_file):
    authentication_request = platform_server_socket.recv(1024).decode()
    if not authentication_request:
        return "No data"

    action, addr_to_check = authentication_request.split("/")
    valid_address = False

    if zero_trust:
        valid_address = True
    else:
        valid_address = True
    
    if valid_address:
        if action == "discover":
            log("Authentication accept to discover request", addr_to_check)
            return "Accepted"
        elif action == "consume":
            log("Authentication accept to consume request", addr_to_check)
            return "Accepted"
        else:
            log("Authentication error", addr_to_check)
            return "Error"
    else:
        log("Authentication reject", addr_to_check)
        return "Rejected"