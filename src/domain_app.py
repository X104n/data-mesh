from config import IP_ADDRESSES
from TUI.main import choose_from_list
from domain.data_product import DataProduct
from domain.artifact import Artifact
import socket

def ip_setup():
    chosen_ip = choose_from_list("Choose an IP address:", IP_ADDRESSES)
    ip = IP_ADDRESSES[chosen_ip]
    return ip

def socket_setup():
    host = ip_setup()
    port = 9000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(10)
    print(f"Listening on {host}:{port}")
    return sock

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
    server = socket_setup()

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