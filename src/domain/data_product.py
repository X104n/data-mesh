from src.TUI.domain_TUI import choose_gateway

class DataProduct:

    def __init__(self, data_id: int, name: str, domain: str, artifacts):
        self.data_id = data_id
        self.name = name
        self.domain = domain
        self.artifacts = artifacts

    # Continue with getters and setters.

    def _get_id(self):
        return self.data_id

    def gateway(self):
        print(choose_gateway(["Gateway 1", "Gateway 2", "Gateway 3"]))