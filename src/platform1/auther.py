import json
from config import IP_ADDRESSES
from .logger import log

def client_authenticate(action, addr_to_check, socket):
    """Authenticate the user based on the action and address"""
    try:
        # Get the platform ip from the JSON file
        with open("src/platform1/marketplace.json", "r") as f:
            marketplace = json.load(f)
        platform_ip = marketplace["platform"]["domain"]

        print(f"Authenticating {addr_to_check} for action {action} with platform {platform_ip}")
        
        socket.connect((platform_ip, 9000))
        socket.sendall("authenticate".encode())
        connection = socket.recv(1024).decode()
        
        if connection == "ok":
            # Send the action and address to check
            auth_msg = f"{action}/{addr_to_check}"
            print(f"Sending authentication message: {auth_msg}")
            socket.sendall(auth_msg.encode())
            
            response = socket.recv(1024).decode()
            print(f"Authentication response: '{response}'")
            
            if response == "ok":
                print(f"User authenticated for action: {action}")
                return True
            else:
                print(f"Authentication failed for action: {action} - response: {response}")
                return False
        else:
            print(f"Error in authentication process - response: {connection}")
            return False
    except Exception as e:
        print(f"Exception during authentication: {e}")
        return False
    finally:
        socket.close()

def server_authenticate(action, socket):
    """Authenticate the user based on the action and address"""
    data = socket.recv(1024).decode()
    if not data:
        return False

    # Split the data into action and address
    action, addr_to_check = data.split("/")
    print(f"Received authentication request for action: {action}")
    print(f"Address to check: {addr_to_check}")

    # Instead of using IP_ADDRESSES, check log.csv for previous discovery activity
    discovered_ips = set()
    try:
        with open("src/platform1/log.csv", "r") as f:
            for line in f:
                parts = line.strip().split(";")
                if len(parts) >= 3:
                    ip = parts[1]
                    message = parts[2]
                    # Check if this IP has successfully discovered before
                    if message.startswith("Discovering") or message == "Authentication accept":
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
