# Portfolio Compliance Checker Solution Design Diagram

## Overview
This diagram shows the main system components, data flows, and MCP integration for the Portfolio Compliance Checker.

```mermaid
flowchart TB
    subgraph App[Core Compliance Application]
        A[Input
        Parser]
        B[Compliance
        Engine]
        C[SQLite
        Persistence]
        D[Reporting
        Generator]
        E[Restricted List
        Loader]
    end

    subgraph MCP[MCP Integration]
        F[MCP Compliance
        Server]
        G[MCP Client]
    end

    subgraph Data[External Inputs]
        I1[CSV / JSON
        Portfolio Files]
        I2[restricted_list.txt]
        I3[SQLite
        Database]
    end

    I1 --> A
    A --> B
    E --> B
    B --> C
    B --> D
    C --> D
    I3 --> C
    I2 --> E

    C -->|store holdings, rules, reports| I3

    B -->|builds verify_ticker status| F
    E -->|restricted stock source| F

    G -->|POST /mcp initialize + tool calls| F
    F -->|verify_ticker result| G

    F -->|HTTP /health| G
    F -->|Streamable HTTP /mcp| G

    style App fill:#f9f,stroke:#333,stroke-width:1px
    style MCP fill:#bbf,stroke:#333,stroke-width:1px
    style Data fill:#efe,stroke:#333,stroke-width:1px
``` 

## Notes
- The Input Parser normalizes portfolio data into internal `Holding` objects.
- The Compliance Engine evaluates ticker holdings against rules and the restricted list.
- SQLite Persistence stores holdings, compliance rules, and generated reports for auditability.
- The MCP Compliance Server exposes `verify_ticker` as a tool via Streamable HTTP.
- The MCP Client uses `ClientSession` with `streamable_http_client` to call the server.
