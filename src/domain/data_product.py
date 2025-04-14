from artifact import artifact

class Data_Product:

    def __init__(self, id, name, domain, artifacts: list[artifact]):
        self.id = id
        self.name = name
        self.domain = domain
        self.artifacts = artifacts

    # Continue with getters and setters.

    def _get_id(self):
        return self.id

    def gateway(self):
        pass