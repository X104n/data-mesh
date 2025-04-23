from config import socket_setup
from domain.data_product import DataProduct
from domain.artifact import Artifact

platform_ip = "localhost"

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

def mesh_hello(domain_client):
    while True:
        domain_client.connect((platform_ip, 9000))
        domain_client.sendall(b"hello")
        data = domain_client.recv(1024)
        if data == b"ok":
            print("Announced presence to the mesh")
            break

def get_mesh(domain_client):
    domain_client.connect((platform_ip, 9000))
    domain_client.sendall(b"get_mesh")
    data = domain_client.recv(1024).decode()
    if data:
        print("Received mesh data:")
        print(data)
    else:
        print("No data received from the mesh")

if __name__ == "__main__":
    #domain_server = socket_setup()
    domain_client = socket_setup(server=False)

    mesh_hello(domain_client)

    get_mesh()