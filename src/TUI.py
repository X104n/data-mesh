"""Terminal user interface"""


def choose_from_list(prompt_text, choices):
    """
    Prompt the user to choose from a list of choices.
    
    Parameters:
        prompt_text (str): Instructions for the user.
        choices (list): A list of options to choose from.
    
    Returns:
        int: Zero-based index of the selected choice.
    """
    print(prompt_text)
    for idx, option in enumerate(choices, start=1):
        print(f"{idx}: {option}")

    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(choices):
                return choice - 1  # convert to zero-based index
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(choices)}.")
        except ValueError:
            print("Please enter a valid number.")