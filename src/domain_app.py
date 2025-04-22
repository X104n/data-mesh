from config import socket_setup
from domain.data_product import DataProduct
from domain.artifact import Artifact

def create_product(number: int):
    data_product = DataProduct(
        data_id=number,
        name=f"Data Product {number}",
        domain=f"Domain {number}",
        artifacts=[],
    )
    return data_product

def create_artifact(number: int, data_product=None, data={"key": "value"}):
    artifact = Artifact(
        data_id=number,
        name=f"Artifact {number}",
        data_product=data_product,
        data=data,
    )
    return artifact

if __name__ == "__main__":
    domain_server = socket_setup()

    domain_client = socket_setup()
    # Connect to the platform server
