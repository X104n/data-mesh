from TUI.main import choose_from_list

class Gateway:

    def __init__(self, gateways: list):
        self.gateways = gateways

    def choose_gateway(self):
        gate = choose_from_list("Choose one gateway: ", self.gateways)
        func = self.gateways[gate]

        method = getattr(self, func, None)
        if method and callable(method):
            method()
        else:
            print(f"{func} is not a valid method.")


    def discover(self):
        print("Discovering...")

    def control(self):
        print("Controlling...")

    def observe(self):
        """May not need this function"""
        print("Observing...")

    def consume(self):
        print("Consuming...")

    def ingest(self):
        print("Ingesting...")