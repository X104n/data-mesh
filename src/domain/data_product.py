from platform_.gateway import Gateway
from config import GATEWAYS

class DataProduct:

    def __init__(self, data_id: int, name: str, domain: str, artifacts):
        self.data_id = data_id
        self.name = name
        self.domain = domain
        self.artifacts = artifacts

        self.gateway = Gateway(GATEWAYS)

    # Continue with getters and setters.

    def _get_id(self):
        return self.data_id

    def access_product(self):
        self.gateway.choose_gateway()