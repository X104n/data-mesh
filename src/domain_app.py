from config import IP_ADDRESSES
from TUI.main import choose_from_list
from domain.data_product import DataProduct
from domain.artifact import Artifact

if __name__ == "__main__":

    # Get the ip address of the machine
    #chosen_ip = choose_from_list("Choose an IP address:", IP_ADDRESSES)
    #ip = IP_ADDRESSES[chosen_ip]

    # Create a data_product
    data_product = DataProduct(
        data_id=1,
        name="Data Product 1",
        domain="Domain 1",
        artifacts=[],
    )

    # Create an Artifact
    artifact1 = Artifact(
        data_id=1,
        name="Artifact 1",
        data_product=data_product,  # This will be set later
        data={"key": "value"},
    )

    # Set the artifact in the data_product

    data_product.artifacts.append(artifact1)

    print(data_product.artifacts[0].data)

    data_product.access_product()