# MCP Design: verify_ticker Tool

## Objective
Create an MCP wrapper around the existing Portfolio Compliance Checker logic that exposes a single tool named `verify_ticker`.
The tool must use the existing `restricted_list.txt` file as the data source for restricted ticker validation.

## Overview
`verify_ticker` will be a lightweight tool that checks whether a ticker symbol is on the restricted list and returns a simple compliance result.
This design reuses the current `load_restricted_list()` logic from `compliance_checker.py` and keeps the tool focused on the restricted-stock rule.

## Tool Specification
- Tool name: `verify_ticker`
- Purpose: validate a single ticker against the restricted-stock list
- Input: JSON object with a single field:
  - `ticker` (string)
- Output: JSON object with fields:
  - `ticker` (string)
  - `compliance_status` (string) — `COMPLIANT` or `NON_COMPLIANT`
  - `violation_details` (string) — empty when compliant
  - `source` (string) — path to `restricted_list.txt`

## Data Source
- `restricted_list.txt` is the authoritative restricted ticker list.
- The tool reads the file once per invocation and normalizes tickers to uppercase.
- The file path is resolved relative to the project root or the running script location.

## Wrapper Design
### verify_ticker flow
1. Accept incoming tool request with `ticker`.
2. Normalize the ticker string:
   - trim whitespace
   - convert to uppercase
3. Load restricted tickers from `_bmad/../restricted_list.txt` or project root `restricted_list.txt`.
4. Match the normalized ticker against the restricted set.
5. Return compliance result:
   - if found: `NON_COMPLIANT` with a restriction reason
   - if not found: `COMPLIANT` with empty violation details

### Implementation options
#### Option A: Minimal wrapper function
- Add a new function in `compliance_checker.py` or a separate module `mcp_tool.py`:
  - `def verify_ticker(ticker: str) -> Dict[str, str]`
- It uses `load_restricted_list()` and direct lookup.
- It does not require full portfolio ingestion.

#### Option B: Reuse ComplianceEngine internals
- Load `restricted_list.txt` into the SQLite `restricted_stocks` table using `SQLiteClient.seed_restricted_stocks()`.
- Instantiate `ComplianceEngine` and evaluate a synthetic `Holding` object.
- This is more aligned with the existing architecture and ensures the tool uses the same rule logic as the portfolio checker.

## Recommended Implementation
Use Option B to preserve architecture consistency:
- Build a synthetic holding for the ticker with default values for the required fields.
- Seed restricted stocks from `restricted_list.txt` into SQLite.
- Initialize `ComplianceEngine` and call `_check_restricted_stock()`.
- Return the result as the tool response.

### Pseudocode
```python
from compliance_checker import (
    SQLiteClient,
    load_restricted_list,
    ComplianceEngine,
    Holding,
    get_db_path,
)


def verify_ticker(ticker: str) -> dict:
    normalized = ticker.strip().upper()
    restricted_stocks = load_restricted_list("restricted_list.txt")
    db = SQLiteClient(get_db_path())
    db.seed_restricted_stocks(restricted_stocks)
    db.seed_compliance_rules()
    engine = ComplianceEngine(db)

    holding = Holding(
        portfolio_id="MCP-VERIFY",
        ticker=normalized,
        asset_class="Unknown",
        quantity=0,
        market_value=0,
        country="",
        sector="",
    )
    violation = engine._check_restricted_stock(holding)
    db.close()

    return {
        "ticker": normalized,
        "compliance_status": "NON_COMPLIANT" if violation else "COMPLIANT",
        "violation_details": violation or "",
        "source": "restricted_list.txt",
    }
```

## Tool Usage Example
Request:
```json
{ "ticker": "PLTR" }
```
Response:
```json
{
  "ticker": "PLTR",
  "compliance_status": "NON_COMPLIANT",
  "violation_details": "Restricted stock: PLTR (Loaded from restricted_list.txt (line 2))",
  "source": "restricted_list.txt"
}
```

## Notes
- This tool intentionally only validates restricted-stock compliance, not full portfolio rules.
- If future MCP tools are added, this design can be extended to support more rule types and broader portfolio evaluation.
- The wrapper should fail clearly if `restricted_list.txt` is missing or unreadable.
