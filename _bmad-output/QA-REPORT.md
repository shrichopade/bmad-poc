# QA Report: Portfolio Compliance Checker

## Review Summary
The implemented `compliance_checker.py` largely fulfills the business requirements from the PRD and architecture.
- CSV and JSON ingestion are supported.
- Compliance rules are defined and evaluated for each holding.
- A pass/fail compliance report is generated with per-holding findings.
- Compliance results and audit records are persisted in SQLite.
- Invalid input is handled with parse error messages.

## Does the code fulfill our business requirements?
Yes, the code meets the core acceptance criteria for the MVP:
1. Portfolio data ingestion from CSV and JSON is supported.
2. Compliance rules are applied and evaluated for each holding.
3. The system prints a readable compliance report.
4. Holding records and reports are saved into SQLite.
5. The report includes overall status and item-level violation details.
6. Parsing failures are reported with clear error messages.

## Bugs and Issues
1. **Duplicate compliance rule seeding:**
   - `seed_compliance_rules()` uses `INSERT OR IGNORE` without a uniqueness constraint on `compliance_rules`.
   - This means repeated runs of the script can create duplicate active rules and duplicate violation messages.

2. **Design deviation from architecture:**
   - The code is implemented as a single monolithic script rather than separated into the modular folder structure described in `architecture.md`.
   - The functional components are present, but the architecture’s intended multi-module layout is not fully realized.

3. **No explicit "ticker not found" state:**
   - The system does not track a separate "not found" status for unknown instruments.
   - A ticker not present in restricted stock data is treated as compliant, which is acceptable but should be documented.

## Suggested Test Cases
### 1. Compliant trade
- `portfolio_id`: `P-200`
- `ticker`: `DEF`
- `asset_class`: `Equity`
- `quantity`: `10`
- `market_value`: `3000`
- `country`: `US`
- `sector`: `Healthcare`

Expected result: `COMPLIANT`, no violation details.

### 2. Violation trade
- `portfolio_id`: `P-200`
- `ticker`: `ABC`
- `asset_class`: `Equity`
- `quantity`: `50`
- `market_value`: `1200`
- `country`: `US`
- `sector`: `Technology`

Expected result: `NON_COMPLIANT`, violation: restricted stock rule triggered because `ABC` is in the restricted stock list.

### 3. Not found trade
- `portfolio_id`: `P-200`
- `ticker`: `UNKNOWN`
- `asset_class`: `Equity`
- `quantity`: `20`
- `market_value`: `2500`
- `country`: `US`
- `sector`: `Technology`

Expected result: `COMPLIANT` (or no restricted-stock violation), because `UNKNOWN` is not in the seeded restricted stock list.

## Recommendations
- Add a unique constraint on `compliance_rules.rule_name` or `rule_type` to prevent duplicate rule inserts.
- Optionally refactor the script into separate modules to match the architecture design more closely.
- Document the handling of "not found" tickers if the domain requires explicit unknown-instrument behavior.
