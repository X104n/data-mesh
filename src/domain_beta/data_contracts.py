"""
Data contracts module for the Beta domain.
Defines the contract for data exchange with the Beta domain.
"""


# This is a placeholder for what would typically be a more complex
# data schema definition, SLO specifications, etc.

# Contract for Beta domain:
#
# Commands:
# - "get_data": Returns a string with Beta's own data
# - "get_analysis:<analysis_id>": Returns a specific analysis by ID
# - "get_combined_data": Returns a combination of Beta's data and Alpha's data
#
# Response Format:
# - All responses are plain text strings
# - Error responses start with "Error: "
#
# SLOs:
# - Response time: < 1 second
# - Availability: 99.9% during test runs
# - Data freshness: Alpha data updated at least every 60 seconds


def get_contract_documentation() -> str:
    """Get documentation for the Beta domain's data contract.

    Returns:
        A string describing the data contract
    """
    return """
    # Beta Domain Data Contract

    ## Commands
    - "get_data": Returns a string with Beta's own data
    - "get_analysis:<analysis_id>": Returns a specific analysis by ID
    - "get_combined_data": Returns a combination of Beta's data and Alpha's data

    ## Response Format
    - All responses are plain text strings
    - Error responses start with "Error: "

    ## Example
    Request: "get_data"
    Response: "Hello from BetaDataProduct! Here's our analysis: ['Beta analysis of Alpha data', 'Another Beta analysis']"

    Request: "get_analysis:analysis1"
    Response: "Beta analysis of Alpha data"

    Request: "get_combined_data"
    Response: "Combined data from Beta and Alpha:
    Beta: ['Beta analysis of Alpha data', 'Another Beta analysis']
    Alpha: Hello from AlphaDataProduct! Here's some data: ['Alpha data point 1', 'Alpha data point 2', 'Alpha data point 3']"
    """