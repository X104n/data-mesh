from TUI.main import choose_from_list

class Gateway:

    def __init__(self, gateways: list):
        self.gateways = gateways

    def choose_gateway(self):
        gate = choose_from_list("Choose one gateway: ", self.gateways)
        func = self.gateways[gate]
        print(func)


    def discover():
        print("Discovering...")

