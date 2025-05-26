import socket

IP_ADDRESSES = [
    "10.0.3.4",
    "10.0.3.5",
    "10.0.3.6",
    "10.0.3.7",
    "10.0.3.8",
    "10.0.3.9",
    "localhost"
]

def choose_from_list(prompt, options):
    print(prompt)
    for idx, option in enumerate(options, start=1):
        print(f"{idx}: {option}")

    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(options):
                return choice - 1  # convert to zero-based index
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(options)}.")
        except ValueError:
            print("Please enter a valid number.")

def ip_setup():
    chosen_ip = choose_from_list("Choose an IP address:", IP_ADDRESSES)
    ip = IP_ADDRESSES[chosen_ip]
    return ip

def socket_setup(server=True):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if server:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host = ip_setup()
        port = 9000
        sock.bind((host, port))
        sock.listen(10)
        print(f"Host and port {host}:{port}")
    return sock