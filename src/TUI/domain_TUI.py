from .main import choose_from_list

def choose_gateway(options):
    return options[choose_from_list("What you want to access:", options)]
