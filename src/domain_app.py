from config import IP_ADDRESSES
from TUI.main import choose_from_list

if __name__ == "__main__":

    # Get the ip address of the machine
    chosen_ip = choose_from_list("Choose an IP address:", IP_ADDRESSES)
    ip = IP_ADDRESSES[chosen_ip]