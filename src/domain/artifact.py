import data_product as dp

class Artifact():

    def __init__(self, id, name, data_product, data: dict):
        
        self.id = id
        self.name = name
        self.data_product = data_product
        self.data = data

    # Continue with getters and setters.

    def private_test():
        return dp._get_private("test")

