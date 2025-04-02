# Data Mesh Socket Demo

This project is a proof-of-concept implementation of a Data Mesh-style network structure using sockets in Python. It is designed purely for research and testing purposes.

## Purpose

The main goal of this project is to demonstrate the architectural concepts of Data Mesh:
- Domain-oriented decentralized data ownership 
- Data as a product
- Self-serve infrastructure
- Federated governance

## Implementation Details

The actual data format (plain text in this case) is not the focus of this implementation. Instead, the project demonstrates how different data domains can communicate with each other using a simple socket-based infrastructure.

## How to Run

To run the demo:

```bash
python src/main.py
```

This will start the data mesh network with domain_alpha serving as a data provider and domain_beta as a consumer.

## Project Structure

- `domain_alpha/` & `domain_beta/`: Represent separate data domains
- `infra/`: Contains shared infrastructure components
- `main.py`: Entry point for running the demo
- `tests/`: Contains test cases

## Note

This is a simplistic implementation intended solely for research and understanding the Data Mesh architecture. It is not production-ready.