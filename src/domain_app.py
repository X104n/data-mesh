import socket
import TUI as tui
from config import IP_ADDRESSES



if __name__ == "__main__":
    
    a = tui.choose_from_list("Choose your ip address", IP_ADDRESSES)
    print(IP_ADDRESSES[a])