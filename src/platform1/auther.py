import json

def client_authenticate(action, addr_to_check, socket):
    """Authenticate the user based on the action and address"""

    # Get the platform ip from the JSON file
    with open("src/platform1/marketplace.json", "r") as f:
        marketplace = json.load(f)
    platform_ip = marketplace["platform"]["domain"]

    socket.connect((platform_ip, 9000))
    socket.sendall("authenticate".encode())
    connection = socket.recv(1024).decode()
    if connection == "ok":
        # Send the action and address to check
        socket.sendall(f"{action}/{addr_to_check}".encode())
        response = socket.recv(1024).decode()
        if response == "ok":
            print(f"User authenticated for action: {action}")
            return True
        else:
            print(f"Authentication failed for action: {action}")
            return False
    else:
        print("Error in authentication process")
        return False

def server_authenticate(action, socket):
    """Authenticate the user based on the action and address"""
    try:
        data = socket.recv(1024).decode()
        if not data:
            return False

        # Split the data into action and address
        action, addr_to_check = data.split("/")
        print(f"Received authentication request for action: {action}")

        # Get the platform ip from the JSON file
        with open("src/platform1/marketplace.json", "r") as f:
            marketplace = json.load(f)

        # Check if the address is in the marketplace JSON file
        if addr_to_check in marketplace:
            if action == "discover":
                print(f"Address {addr_to_check} is eligible for discovery")
                socket.sendall(b"ok")
                return True
            elif action == "consume":
                print(f"Address {addr_to_check} is eligible for consumption")
                socket.sendall(b"ok")
                return True
            socket.sendall(b"error")
            return False
        else:
            print(f"Address {addr_to_check} is not in the marketplace")
            socket.sendall(b"error")
            return False
    except Exception as e:
        print(f"Error in authentication process: {e}")
        return False
    