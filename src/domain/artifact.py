class Artifact:
    def __init__(self, data_id: int, name: str, data_product=None, data=None):
        self.data_id = data_id
        self.name = name
        self.data_product = data_product
        self.data = data if data else {}
    
    def to_dict(self):
        """Convert Artifact to dictionary for JSON serialization"""
        return {
            "data_id": self.data_id,
            "name": self.name,
            "data": self.data
        }
