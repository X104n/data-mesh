import json
from .logger import log
from collections import deque

def client_authenticate(action, addr_to_check, socket):
    try:
        with open("src/platform_code/marketplace.json", "r") as f:
            marketplace = json.load(f)
        platform_ip = marketplace["platform"]["domain"]
        
        socket.connect((platform_ip, 9000))
        socket.sendall("authenticate".encode())
        request_received = socket.recv(1024).decode()
        
        if request_received == "ok":
            auth_msg = f"{action}/{addr_to_check}"
            socket.sendall(auth_msg.encode())
            
            auth_response = socket.recv(1024).decode()
            if auth_response == "ok":
                return True
            elif auth_response == "authentication failed":
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
        socket.close()

def server_authenticate(socket, zero_trust, log_file):
    authentication_request = socket.recv(1024).decode()
    if not authentication_request:
        return False

    action, addr_to_check = authentication_request.split("/")
    valid_address = False

    if zero_trust:
        last_lines = deque(log_file, 10_000)
        last_lines = [line.strip().split(";") for line in last_lines]
    
        for line in last_lines:
            if line[1] == addr_to_check:
                if line[2] == "Hello":
                    valid_address = True
    else:
        valid_address = True
    
    if valid_address:
        if action == "discover":
            log("Authentication accept to discover request", addr_to_check)
            return True
        elif action == "consume":
            log("Authentication accept to consume request", addr_to_check)
            return True
        else:
            socket.sendall(b"error")
            log("Authentication error", addr_to_check)
            return False
    else:
        log("Authentication reject", addr_to_check)
        socket.sendall(b"authentication failed")
        return False