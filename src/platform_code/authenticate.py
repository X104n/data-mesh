import json
from .logger import log
from collections import deque

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
                print(f"Authentication successful for action: {action}")
                return True
            elif auth_response == "authentication rejected":
                print(f"Authentication rejected for action: {action}")
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
        # Reset file pointer to the beginning before reading
        log_file.seek(0)
        
        # Now read the contents
        last_lines = list(log_file)
        print(f"Last lines from file: {last_lines}")
        
        # Parse the lines
        last_lines = [line.strip().split(";") for line in last_lines if line.strip()]
        print(f"Parsed lines: {last_lines}")
        
        for line in last_lines:
            if len(line) >= 3 and line[1] == addr_to_check:
                print(f"Found matching address: {addr_to_check}")
                if line[2] == "Hello":
                    print(f"Hello message found for address: {addr_to_check}")
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