"""Terminal user interface"""


def choose_ip ():
    """Return what IP address to use for the server"""
    from config import IP_ADDRESSES as adresses

    # Display the available adresses with their indices
    print("Please select from the following adresses:")
    for i, option in enumerate(adresses):
        print(f"{i}: {option}")
    
    # Get and validate user input
    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 0 <= choice < len(adresses):
                return adresses[choice]
            else:
                print(f"Invalid choice. Please enter a number between 0 and {len(adresses)-1}.")
        except ValueError:
            print("Please enter a valid number.")
