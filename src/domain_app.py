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

    # Make products
    data_product = create_product(1)

    # Make artifacts
    artifact1 = create_artifact(1, data_product, {"key": "value1"})
    artifact2 = create_artifact(2, data_product, {"key": "value2"})
    artifact3 = create_artifact(3, data_product, {"key": "value3"})

    # Set the artifact in the data_product
    data_product.artifacts.append(artifact1)
    data_product.artifacts.append(artifact2)
    data_product.artifacts.append(artifact3)

    print(data_product.artifacts[0].data)

    data_product.access_product()