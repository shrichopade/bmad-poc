# Portfolio Compliance Checker PRD

## Overview
This PRD defines the Portfolio Compliance Checker, a Python-based tool that assesses investment portfolios against regulatory and internal policy rules and produces clear compliance results for each position.

## User Stories
- As a Compliance Officer, I want to upload a portfolio file so I can evaluate current holdings against compliance rules.
- As a Risk Analyst, I want the system to flag rule violations so I can take corrective action on non-compliant positions.
- As an Audit Manager, I want compliance results stored in SQLite so I can review historical decision records.
- As an Operations Lead, I want a clear summary report so I can quickly understand portfolio compliance status.

## Data Schema
### CSV Input Schema
- `portfolio_id` (string): Unique portfolio identifier.
- `ticker` (string): Security ticker symbol.
- `asset_class` (string): Asset class designation (e.g., Equity, Fixed Income).
- `quantity` (number): Number of shares or units held.
- `market_value` (number): Current market value of the holding.
- `country` (string): Country of issuer or domicile.
- `sector` (string): Industry sector.

### SQL Table Schema
Table: `portfolio_holdings`
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `portfolio_id` TEXT NOT NULL
- `ticker` TEXT NOT NULL
- `asset_class` TEXT
- `quantity` REAL
- `market_value` REAL
- `country` TEXT
- `sector` TEXT
- `compliance_status` TEXT
- `violation_details` TEXT
- `evaluated_at` TEXT

Table: `compliance_rules`
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `rule_name` TEXT NOT NULL
- `rule_type` TEXT NOT NULL
- `threshold` REAL
- `parameters` TEXT
- `active` INTEGER

Table: `compliance_reports`
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `portfolio_id` TEXT NOT NULL
- `report_date` TEXT NOT NULL
- `overall_status` TEXT
- `summary` TEXT
- `created_at` TEXT

## Acceptance Criteria
1. Portfolio data can be ingested from CSV and JSON inputs.
2. Compliance rules can be defined and evaluated for each holding.
3. The system generates a pass/fail compliance report with identifiable rule violations.
4. Compliance results and audit records are stored in SQLite.
5. Reports include overall portfolio status and specific findings for non-compliant assets.
6. The tool handles invalid input gracefully and reports parse errors clearly.

## Notes
- Focus on a minimal viable implementation first: CSV ingestion, rule evaluation, reporting, and SQLite persistence.
- Ensure the output report is easy for non-technical stakeholders to interpret.
