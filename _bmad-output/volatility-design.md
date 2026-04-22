# Volatility Tool Design for Portfolio Compliance MCP Server

## Overview
Design a second MCP tool for the existing `Portfolio Compliance MCP Server` named `check_volatility`.
This tool accepts a single input, `ticker`, and returns a deterministic mock volatility assessment.

## Tool Definition
- Tool name: `check_volatility`
- Title: `Check Volatility`
- Description: `Return a mock volatility rating for a stock ticker and its stability status.`

## Input
- `ticker` (string)
  - Required
  - Normalized by trimming whitespace and upper-casing
  - Reject empty or non-string values with a clear error

## Output
Return a JSON-compatible dictionary with the following fields:
- `ticker`: normalized ticker symbol
- `volatility`: one of `LOW`, `MEDIUM`, or `HIGH`
- `status`: one of `STABLE`, `NEUTRAL`, or `VOLATILE`

Example outputs:
- `{ "volatility": "LOW", "status": "STABLE" }`
- `{ "volatility": "HIGH", "status": "VOLATILE" }`
- `{ "volatility": "MEDIUM", "status": "NEUTRAL" }`

## Mock Logic
- If `ticker` is `AAPL` or `MSFT`
  - Return `{ "volatility": "LOW", "status": "STABLE" }`
- If `ticker` is `TSLA` or `COIN`
  - Return `{ "volatility": "HIGH", "status": "VOLATILE" }`
- Otherwise
  - Return `{ "volatility": "MEDIUM", "status": "NEUTRAL" }`

## Integration with Existing Server
Based on the existing `mcp_compliance_server.py` design:
- Use `FastMCP` and the `@server.tool(...)` decorator to register the tool
- Add a new helper function `check_volatility(ticker: str) -> Dict[str, str]`
- Add a new wrapper function `check_volatility_tool(ticker: str) -> Dict[str, str]`
- Keep the same transport support (`streamable-http` and `stdio`)
- Update the root service metadata to include `check_volatility` in the `tools` list

## Example Implementation Sketch
```python
@server.tool(
    name="check_volatility",
    title="Check Volatility",
    description="Return a mock volatility rating for a stock ticker and its stability status.",
)
def check_volatility_tool(ticker: str) -> Dict[str, str]:
    normalized = ticker.strip().upper()
    if normalized in {"AAPL", "MSFT"}:
        return {"ticker": normalized, "volatility": "LOW", "status": "STABLE"}
    if normalized in {"TSLA", "COIN"}:
        return {"ticker": normalized, "volatility": "HIGH", "status": "VOLATILE"}
    return {"ticker": normalized, "volatility": "MEDIUM", "status": "NEUTRAL"}
```

## Notes
- This design keeps the new tool intentionally simple and aligned with the existing MCP wrapper pattern.
- The new tool is a second MCP tool alongside `verify_ticker`, enabling the server to support both compliance validation and volatility assessment.
