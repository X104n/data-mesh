import platform1.gateway as gateway
from config import GATEWAYS

class DataProduct:

    def __init__(self, data_id: int, name: str, domain: str, artifacts):
        self.data_id = data_id
        self.name = name
        self.domain = domain
        self.artifacts = artifacts

        gateway.discover_registration(self)


        

    # Continue with getters and setters.

    def _get_id(self):
        return self.data_id