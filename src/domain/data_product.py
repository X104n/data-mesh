from artifact import artifact

class Data_Product:

    def __init__(self, id, name, domain, data, artifacts: list[artifact]):
        self.id = id
        self.name = name
        self.domain = domain
        self.data = data
        self.artifacts = artifacts

    # Continue with getters and setters.