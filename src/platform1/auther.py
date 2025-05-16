import json
from .logger import log
from collections import deque

def client_authenticate(action, addr_to_check, socket):
    try:
        with open("src/platform1/marketplace.json", "r") as f:
            marketplace = json.load(f)
        platform_ip = marketplace["platform"]["domain"]

        print(f"Authenticating {addr_to_check} for action {action} with platform {platform_ip}")
        
        socket.connect((platform_ip, 9000))
        socket.sendall("authenticate".encode())
        request_received = socket.recv(1024).decode()
        
        if request_received == "ok":
            
            auth_msg = f"{action}/{addr_to_check}"
            socket.sendall(auth_msg.encode())
            
            auth_response = socket.recv(1024).decode()
            print(f"Authentication response: '{auth_response}'")
            
            if auth_response == "ok":
                print(f"User authenticated for action: {action}")
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
        socket.close()

def server_authenticate(action, socket):
    
    data = socket.recv(1024).decode()
    if not data:
        return False

    # Split the data into action and address
    action, addr_to_check = data.split("/")
    print(f"Received authentication request for action: {action}")
    print(f"Address to check: {addr_to_check}")

    # Check only the last 1,000 lines of log.csv
    discovered_ips = set()
    try:
        # Use deque with maxlen to only keep the last 1,000 lines
        last_lines = deque(maxlen=1_000)
        with open("src/platform1/log.csv", "r") as f:
            for line in f:
                last_lines.append(line)
        
        # Process only the lines in our deque
        for line in last_lines:
            parts = line.strip().split(";")
            if len(parts) >= 3:
                ip = parts[1]
                message = parts[2]

                if message == "Hello":
                    discovered_ips.add(ip)
    except FileNotFoundError:
        print("Log file not found. Authentication will fail.")
    
    
    # Check if the address has previously discovered products
    if addr_to_check in discovered_ips:
        if action == "discover":
            print(f"Address {addr_to_check} is eligible for discovery")
            log("Authentication accept", addr_to_check)
            return True
        elif action == "consume":
            print(f"Address {addr_to_check} is eligible for consumption")
            log("Authentication accept", addr_to_check)
            return True
        socket.sendall(b"error")
        log("Authentication error", addr_to_check)
        return False
    else:
        print(f"Address {addr_to_check} has no record of discovery in logs")
        log("Authentication reject", addr_to_check)
        socket.sendall(b"error")
        return False
