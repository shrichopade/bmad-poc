from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import anyio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

ROOT = Path(__file__).resolve().parent
SERVER_SCRIPT = ROOT / "mcp_compliance_server.py"
TICKERS = ["AAPL", "TSLA", "MSFT", "XYZ"]


def format_decision(compliance_status: str, volatility: str) -> str:
    normalized_status = compliance_status.strip().upper()
    normalized_volatility = volatility.strip().upper()

    if normalized_status == "NON_COMPLIANT" or normalized_volatility == "HIGH":
        return "REJECT"
    if normalized_status == "COMPLIANT" and normalized_volatility == "LOW":
        return "STRONG BUY"
    if normalized_status == "COMPLIANT" and normalized_volatility == "MEDIUM":
        return "HOLD"
    return "REJECT"


def normalize_tool_result(result: Any) -> dict[str, Any]:
    if hasattr(result, "result"):
        raw = getattr(result, "result")
        if isinstance(raw, dict):
            return raw
        return raw if isinstance(raw, dict) else {"result": str(raw)}
    if hasattr(result, "structuredContent") and result.structuredContent is not None:
        return result.structuredContent
    if hasattr(result, "model_dump"):
        return result.model_dump()
    return result if isinstance(result, dict) else {"result": str(result)}


def print_investment_report(rows: list[dict[str, str]]) -> None:
    header = "Ticker  | Compliance     | Volatility | Recommendation"
    separator = "-------+----------------+------------+------------------"
    print("\nInvestment Report")
    print(separator)
    print(header)
    print(separator)
    for row in rows:
        print(
            f"{row['ticker']:<7}| {row['compliance_status']:<14}| {row['volatility']:<10}| {row['recommendation']}",
        )
    print(separator)


async def run_portfolio_advisor() -> None:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-u", str(SERVER_SCRIPT), "--stdio"],
        cwd=str(ROOT),
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as client:
            await client.initialize()

            report_rows: list[dict[str, str]] = []

            for ticker in TICKERS:
                verify_result = await client.call_tool("verify_ticker", {"ticker": ticker})
                print(f"[DEBUG] verify_ticker raw response for {ticker}: {verify_result!r}")
                if verify_result.isError:
                    report_rows.append(
                        {
                            "ticker": ticker,
                            "compliance_status": "ERROR",
                            "volatility": "ERROR",
                            "recommendation": "REJECT",
                        }
                    )
                    continue

                verify_output = normalize_tool_result(verify_result)
                print(f"[DEBUG] verify_ticker parsed JSON for {ticker}: {verify_output!r}")
                compliance_status = str(verify_output.get("compliance_status", "UNKNOWN"))

                volatility_result = await client.call_tool("check_volatility", {"ticker": ticker})
                print(f"[DEBUG] check_volatility raw response for {ticker}: {volatility_result!r}")
                if volatility_result.isError:
                    report_rows.append(
                        {
                            "ticker": ticker,
                            "compliance_status": compliance_status,
                            "volatility": "ERROR",
                            "recommendation": "REJECT",
                        }
                    )
                    continue

                volatility_output = normalize_tool_result(volatility_result)
                print(f"[DEBUG] check_volatility parsed JSON for {ticker}: {volatility_output!r}")
                volatility = str(volatility_output.get("volatility", "UNKNOWN"))

                report_rows.append(
                    {
                        "ticker": ticker,
                        "compliance_status": compliance_status,
                        "volatility": volatility,
                        "recommendation": format_decision(compliance_status, volatility),
                    }
                )

            print_investment_report(report_rows)


if __name__ == "__main__":
    anyio.run(run_portfolio_advisor)
