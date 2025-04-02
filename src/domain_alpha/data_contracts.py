"""
Data contracts module for the Alpha domain.
Defines the contract for data exchange with the Alpha domain.
"""


# This is a placeholder for what would typically be a more complex
# data schema definition, SLO specifications, etc.

# Contract for Alpha domain:
#
# Commands:
# - "get_data": Returns a string with all data from the Alpha domain
# - "get_item:<item_id>": Returns a specific data item by ID
#
# Response Format:
# - All responses are plain text strings
# - Error responses start with "Error: "
#
# SLOs:
# - Response time: < 1 second
# - Availability: 99.9% during test runs


def get_contract_documentation() -> str:
    """Get documentation for the Alpha domain's data contract.

    Returns:
        A string describing the data contract
    """
    return """
    # Alpha Domain Data Contract

    ## Commands
    - "get_data": Returns a string with all data from the Alpha domain
    - "get_item:<item_id>": Returns a specific data item by ID

    ## Response Format
    - All responses are plain text strings
    - Error responses start with "Error: "

    ## Example
    Request: "get_data"
    Response: "Hello from AlphaDataProduct! Here's some data: ['Alpha data point 1', 'Alpha data point 2', 'Alpha data point 3']"

    Request: "get_item:item1"
    Response: "Alpha data point 1"
    """