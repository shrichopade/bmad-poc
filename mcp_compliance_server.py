import argparse
import os
from typing import Dict

from starlette.responses import JSONResponse
from mcp.server.fastmcp import FastMCP

from compliance_checker import (
    ComplianceEngine,
    Holding,
    SQLiteClient,
    get_db_path,
    load_restricted_list,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESTRICTED_LIST_FILENAME = "restricted_list.txt"
RESTRICTED_LIST_PATH = os.path.join(BASE_DIR, RESTRICTED_LIST_FILENAME)


def resolve_restricted_list_path() -> str:
    if os.path.exists(RESTRICTED_LIST_PATH):
        return RESTRICTED_LIST_PATH
    raise FileNotFoundError(
        f"Restricted list not found at {RESTRICTED_LIST_PATH}."
    )


def verify_ticker(ticker: str) -> Dict[str, str]:
    if not isinstance(ticker, str):
        raise ValueError("ticker must be a string")

    normalized = ticker.strip().upper()
    if not normalized:
        raise ValueError("ticker must not be empty")

    restricted_list_path = resolve_restricted_list_path()
    restricted_stocks = load_restricted_list(restricted_list_path)

    db = SQLiteClient(get_db_path())
    try:
        db.seed_restricted_stocks(restricted_stocks)
        db.seed_compliance_rules()
        engine = ComplianceEngine(db)
        holding = Holding(
            portfolio_id="MCP-VERIFY",
            ticker=normalized,
            asset_class="Unknown",
            quantity=0.0,
            market_value=0.0,
            country="",
            sector="",
        )
        violation = engine._check_restricted_stock(holding)
    finally:
        db.close()

    return {
        "ticker": normalized,
        "compliance_status": "NON_COMPLIANT" if violation else "COMPLIANT",
        "violation_details": violation or "",
        "source": restricted_list_path,
    }


def check_volatility(ticker: str) -> Dict[str, str]:
    if not isinstance(ticker, str):
        raise ValueError("ticker must be a string")

    normalized = ticker.strip().upper()
    if not normalized:
        raise ValueError("ticker must not be empty")

    if normalized in {"AAPL", "MSFT"}:
        return {"ticker": normalized, "volatility": "LOW", "status": "STABLE"}
    if normalized in {"TSLA", "COIN"}:
        return {"ticker": normalized, "volatility": "HIGH", "status": "VOLATILE"}
    return {"ticker": normalized, "volatility": "MEDIUM", "status": "NEUTRAL"}


server = FastMCP(
    name="Portfolio Compliance MCP Server",
    instructions="Provide a verify_ticker tool for restricted stock compliance checks.",
    host="127.0.0.1",
    port=8000,
)


@server.tool(
    name="verify_ticker",
    title="Verify Ticker",
    description="Check whether a ticker is on the restricted stock list and return compliance status.",
)
def verify_ticker_tool(ticker: str) -> Dict[str, str]:
    return verify_ticker(ticker)


@server.tool(
    name="check_volatility",
    title="Check Volatility",
    description="Return a mock volatility rating for a stock ticker and its stability status.",
)
def check_volatility_tool(ticker: str) -> Dict[str, str]:
    return check_volatility(ticker)


@server.custom_route("/", methods=["GET"])
async def root(request) -> JSONResponse:
    return JSONResponse(
        {
            "service": "Portfolio Compliance MCP Server",
            "status": "running",
            "tools": ["verify_ticker", "check_volatility"],
            "documentation": "Use the MCP streamable HTTP endpoint for tool calls.",
        }
    )


@server.custom_route("/health", methods=["GET"])
async def health(request) -> JSONResponse:
    return JSONResponse({"status": "healthy", "uptime": "ok"})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start the MCP compliance server")
    parser.add_argument(
        "--stdio",
        action="store_true",
        help="Run the server on stdio transport for MCP client integration",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    transport = "stdio" if args.stdio else "streamable-http"
    server.run(transport=transport)


if __name__ == "__main__":
    main()
