# Distributed Data Mesh System

This repository contains a distributed data mesh implementation developed as part of a master's thesis research project. The system demonstrates a decentralized architecture where multiple domain nodes can register, discover, and consume data products through a central platform service.

## System Overview

The system consists of two main components:

- **Platform/Server Node**: Acts as a central registry and authentication service for the data mesh
- **Domain Nodes**: Independent services that can both provide and consume data products

The architecture supports both zero-trust and traditional IP-based authentication mechanisms, allowing for comprehensive security analysis and performance comparison.

## Network Requirements

This system is designed to run on **different machines within the same IPv4 local network**. You need:

- **Minimum 3 machines**: 1 platform server + 2 domain nodes
- **Recommended**: 3-6 machines for comprehensive testing
- All machines must be on the same local network segment
- Each machine should have Python 3.x installed

## Setup Instructions

### 1. Configure IP Addresses

Before running the system, you must configure the IP addresses in `src/config.py` to match your network setup:

```python
IP_ADDRESSES = [
    "10.0.3.4",    # Add your actual machine IPs here
    "10.0.3.5", 
    "10.0.3.6",
    "10.0.3.7",
    "10.0.3.8",
    "10.0.3.9",
    "localhost"    # Keep for local testing
]
```

**Important**: Replace these IP addresses with the actual IPv4 addresses of the machines in your network where you plan to run the system.

### 2. Distribute Code

Copy this repository to all machines that will participate in the data mesh.

### 3. Running the System

#### On the Platform/Server Machine:
```bash
cd src/
python platform_app.py
```

When prompted, choose whether to enable zero-trust authentication (y/n).

#### On Domain Machines:
```bash
cd src/
python domain_app.py
```

When prompted:
- Choose whether to enable zero-trust authentication (y/n) - should match platform setting
- The system will automatically start discovering and consuming data products from other domains

## System Behavior

1. **Domain Registration**: Each domain node registers itself with the platform and announces its data products
2. **Service Discovery**: Domains can discover available data products across the mesh
3. **Data Consumption**: Domains consume data products from other domains for a specified number of iterations (configurable in `domain_app.py`)
4. **Performance Monitoring**: The system logs response times and success/failure rates for each iteration

## Authentication Modes

### Zero-Trust Mode
- All requests are authenticated through the platform
- Enhanced security with centralized policy enforcement
- Additional network overhead due to authentication requests

### Traditional IP-Based Mode
- Authentication based on predefined IP address allowlists
- Lower latency but reduced security granularity
- Suitable for trusted network environments

## Performance Analysis

The system automatically collects performance metrics:

- **Domain metrics** (`domain_app.csv`): Response times, success/failure rates
- **Platform logs** (`platform_code/log.csv`): Authentication and discovery request logs

## Research Data

This repository includes simulation data from comprehensive testing conducted for the master's thesis research. The results can be found in the `simulation_data/` directory, containing:

### Test Configurations
- **6 total simulations** conducted on 6 machines
- **Zero-trust vs Non-zero-trust** authentication (3 simulations each)
- **Variable load testing**: 1, 3, and 5 consuming domains per configuration

Each simulation generated network traffic patterns for performance analysis

### Data Files
The simulation data includes `domain_app.csv` outputs from each test configuration, providing:
- Response time measurements
- Success/failure rates
- Network performance under different security and load conditions

## File Structure

```
src/
├── domain_app.py          # Main domain node application
├── platform_app.py       # Main platform server application
├── average.py            # Performance analysis tool
├── config.py             # Network configuration
├── domain/               # Domain-specific classes
│   ├── artifact.py
│   ├── data_product.py
│   └── local_db.json
└── platform_code/       # Platform implementation
    ├── authenticate.py
    ├── gateway.py
    ├── logger.py
    ├── marketplace.json
    └── log.csv
```

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure all IP addresses in `config.py` are correct and accessible
2. **No Products Found**: Verify that domain nodes have successfully registered with the platform
3. **Authentication Failures**: Ensure zero-trust settings match between platform and domains

### Network Connectivity
- Test connectivity between machines using `ping` before running the system
- Ensure firewall settings allow traffic on port 9000
- Verify all machines are on the same network segment

## Research Context

This system was developed as part of a master's thesis investigating distributed data mesh architectures, with particular focus on:

- Performance implications of zero-trust authentication in distributed systems
- Scalability characteristics under varying network loads
- Comparative analysis of security vs. performance trade-offs

The collected simulation data provides empirical evidence for thesis conclusions regarding distributed data mesh performance under different operational conditions.

## Usage Notes

- Domain nodes will run for a specified number of iterations (default: 1,000,000) as defined in the for loop in `domain_app.py`
- You can modify the iteration count by changing the range in: `for i in range(0, 1_000_000):`
- Press `Ctrl+C` to shutdown any component before completion
- Monitor the CSV output files for real-time performance metrics
- Each domain generates synthetic data products for testing purposes