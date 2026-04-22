from pathlib import Path
from typing import Any

import anyio
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

ROOT = Path(__file__).resolve().parent
SERVER_URL = "http://127.0.0.1:8000/mcp"


async def run_client() -> None:
    async with streamable_http_client(SERVER_URL) as (read_stream, write_stream, _):
        # ClientSession must be entered as an async context manager so its
        # receive loop starts and incoming responses can be processed.
        async with ClientSession(read_stream, write_stream) as client:
            await client.initialize()

            rows = []

            for ticker in ["AAPL", "TSLA"]:
                result = await client.call_tool("verify_ticker", {"ticker": ticker})
                if result.isError:
                    print(f"{ticker}: ERROR -> {result.model_dump()}")
                    continue

                output = result.structuredContent or result.model_dump()
                if isinstance(output, dict) and "result" in output:
                    output = output["result"]

                ticker_value = output.get("ticker", ticker)
                compliance_status = output.get("compliance_status", "UNKNOWN")
                violation_details = output.get("violation_details", "")
                source = output.get("source", "")

                rows.append([ticker_value, compliance_status, violation_details, source])

            if rows:
                headers = ["Ticker", "Compliance Status", "Violation Details", "Source"]
                widths = [max(len(str(cell)) for cell in column) for column in zip(headers, *rows)]
                header_line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
                separator_line = "-+-".join("-" * w for w in widths)
                print(header_line)
                print(separator_line)
                for row in rows:
                    print(" | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row)))


if __name__ == "__main__":
    anyio.run(run_client)
