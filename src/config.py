"""Configuration file"""


IP_ADDRESSES = [
    "10.0.3.4",
    "10.0.3.5",
    "10.0.3.6",
    "10.0.3.7"
]

GATEWAYS = [
    "discover", # Use this to discover data products in the data mesh domain 
    "control", # Use this to control the data product such as start, stop, restart
    "observe", # Use this to observe like the healt and status of the data product (may not need this)
    "consume", # Use this to consume the data product (read only)
    "ingest" # Use this to ingest data into the data product (write only)
]