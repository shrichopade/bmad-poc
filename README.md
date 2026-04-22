# BMAD PoC - AI Agent with Compliance Framework

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-brightgreen) 

A proof-of-concept implementation of the BMAD methodology for building intelligent AI agents with built-in compliance checking and portfolio advisory capabilities.

## Overview

BMAD PoC demonstrates how to construct a sophisticated AI agent that integrates compliance validation, portfolio analysis, and Model Context Protocol (MCP) communication. This project showcases best practices for building agents that must operate within regulatory constraints while providing intelligent financial advisory services.

## Features

* ✅ **BMAD Methodology Implementation** - Structured approach to AI agent design following the BMAD framework principles

* ✅ **Compliance Checking** - Real-time validation against restricted lists and compliance rules

* ✅ **Portfolio Advisory** - Intelligent portfolio analysis and recommendations

* ✅ **MCP Integration** - Model Context Protocol client and server for seamless communication

* ✅ **SQLite Database** - Persistent storage for compliance data and trading records

* ✅ **Trade Logging** - Comprehensive CSV-based trade history tracking

* ✅ **Modular Architecture** - Clean separation of concerns for easy extension and testing

## Quick Start

Get up and running in 2 minutes:

```bash
# Clone the repository
git clone https://github.com/shrichopade/bmad-poc.git

# Navigate to directory
cd bmad-poc

# Install dependencies
pip install -r requirements.txt

# Run the portfolio advisor
python portfolio_advisor.py
```

## Installation

### Prerequisites

* Python 3.8 or higher

* pip (Python package manager)

* SQLite3 (usually included with Python)

### Steps

1. **Clone the repository**

```bash
git clone https://github.com/shrichopade/bmad-poc.git
cd bmad-poc
```

20. **Create a virtual environment (recommended)**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

30. **Install dependencies**

```bash
pip install -r requirements.txt
```

40. **Verify installation**

```bash
python -c "import sys; print(f'Python {sys.version}')"
```

## Usage

### Running the Portfolio Advisor

The main entry point for the AI agent:

```bash
python portfolio_advisor.py
```

This starts the portfolio advisor agent which can:

* Analyze investment portfolios

* Validate trades against compliance rules

* Provide portfolio recommendations

* Interact via the MCP protocol

### Starting the MCP Compliance Server

Run the compliance checking server:

```bash
python mcp_compliance_server.py
```

This server provides:

* Real-time compliance validation

* Restricted entity checking

* Trade validation against compliance rules

### Using the MCP Client

Connect to the compliance server:

```bash
python mcp_client.py
```

The client can send compliance queries and receive validation responses.

### Running Compliance Checks

The compliance checker validates trades and entities:

```bash
python compliance_checker.py
```

This tool:

* Loads restricted entities from `restricted_list.txt`

* Validates trades in `trades.csv`

* Stores results in `compliance.db`

* Generates compliance reports

## Architecture

### Core Components

**portfolio_advisor.py**

* Main AI agent implementation

* Orchestrates portfolio analysis and advisory

* Integrates with compliance checking system

**mcp_client.py**

* Model Context Protocol client

* Communicates with the compliance server

* Handles request/response serialization

**mcp_compliance_server.py**

* MCP-compatible compliance validation server

* Provides compliance checking endpoints

* Manages restricted entity database

**compliance_checker.py**

* Compliance validation engine

* Processes trade data

* Manages SQLite compliance database

### Data Files

* **compliance.db** - SQLite database storing compliance rules and validation history

* **trades.csv** - Trade transaction data for analysis and validation

* **restricted_list.txt** - List of restricted entities and counterparties

* **server.log** - Server operation logs

## Configuration

### Restricted Entities

Edit `restricted_list.txt` to define entities that cannot be traded with:

```
ENTITY_NAME_1
ENTITY_NAME_2
SANCTIONED_ENTITY_3
```

### Trade Data

Add trades to `trades.csv` with the following format:

```
trade_id,counterparty,security,quantity,price,date
T001,ENTITY_A,AAPL,100,150.00,2024-01-15
T002,ENTITY_B,GOOGL,50,2800.00,2024-01-16
```

## API Reference

### Compliance Checker

```python
from compliance_checker import ComplianceChecker

checker = ComplianceChecker()

# Validate a trade
is_compliant = checker.validate_trade(
    counterparty="ENTITY_A",
    security="AAPL",
    quantity=100,
    price=150.00
)

# Check if entity is restricted
is_restricted = checker.is_restricted(entity_name="ENTITY_A")
```

### Portfolio Advisor

```python
from portfolio_advisor import PortfolioAdvisor

advisor = PortfolioAdvisor()

# Get portfolio analysis
analysis = advisor.analyze_portfolio(portfolio_data)

# Get recommendations
recommendations = advisor.get_recommendations(portfolio_data)
```

### MCP Client

```python
from mcp_client import MCPClient

client = MCPClient(host="localhost", port=8000)

# Send compliance check request
response = client.check_compliance(entity="ENTITY_A")

# Get validation result
is_valid = response['is_compliant']
```

## Testing

```bash
# Run compliance validation
python compliance_checker.py

# Run MCP server
python mcp_compliance_server.py

# In another terminal, run MCP client
python mcp_client.py
```

## Project Structure

```
bmad-poc/
├── portfolio_advisor.py          # Main AI agent
├── mcp_client.py                 # MCP client implementation
├── mcp_compliance_server.py       # MCP compliance server
├── compliance_checker.py          # Compliance validation engine
├── compliance.db                  # SQLite compliance database
├── trades.csv                     # Trade transaction data
├── restricted_list.txt            # Restricted entities list
├── server.log                     # Server logs
├── _bmad/                         # BMAD methodology files
├── _bmad-output/                  # Generated outputs
└── __pycache__/                   # Python cache
```

## Roadmap

* Web UI dashboard for portfolio visualization

* Real-time market data integration

* Advanced risk analytics

* Multi-currency support

* Audit trail and compliance reporting

* REST API endpoints

* Machine learning-based recommendations

* Integration with external compliance databases

See [issues](https://github.com/shrichopade/bmad-poc/issues) for full list of proposed features and known issues.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository

2. Create a feature branch (`git checkout -b feature/amazing-feature`)

3. Commit your changes (`git commit -m 'Add amazing feature'`)

4. Push to the branch (`git push origin feature/amazing-feature`)

5. Open a Pull Request

### Development Guidelines

* Follow PEP 8 style guidelines

* Add docstrings to all functions and classes

* Write unit tests for new features

* Update documentation as needed

* Keep commits atomic and well-described

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

* BMAD Methodology framework

* Model Context Protocol specification

* Contributors and community feedback

* Python ecosystem libraries

## Support

* 🐛 **Issues**: [GitHub Issues](https://github.com/shrichopade/bmad-poc/issues)

* 📧 **Email**: [Contact via GitHub](https://github.com/shrichopade)

* 💬 **Discussions**: [GitHub Discussions](https://github.com/shrichopade/bmad-poc/discussions)

## Authors

* **Shrikant Chopade** - *Initial work and maintenance* - [GitHub](https://github.com/shrichopade)

See also the list of [contributors](https://github.com/shrichopade/bmad-poc/contributors) who participated in this project.

---

Made with ❤️ by Shrikant Chopade
