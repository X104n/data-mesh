class DataProduct:
    def __init__(self, data_id: int, name: str, domain: str, artifacts):
        self.data_id = data_id
        self.name = name
        self.domain = domain
        self.artifacts = artifacts
    
    def to_dict(self):
        return {
            "data_id": self.data_id,
            "name": self.name,
            "domain": self.domain,
            "artifacts": [artifact.to_dict() for artifact in self.artifacts]
        }
