# Portfolio Compliance Checker Architecture

## System Components

### 1. Input Parser
- Responsible for ingesting portfolio data from CSV and JSON.
- Validates required fields: `portfolio_id`, `ticker`, `asset_class`, `quantity`, `market_value`, `country`, `sector`.
- Normalizes raw input into a common internal model for the Logic Engine.
- Produces clear parse error messages for invalid input.

### 2. Logic Engine
- Evaluates each holding against compliance rules.
- Supports rule types such as concentration limits, prohibited asset classes, position size thresholds, and sector/country restrictions.
- Assigns `compliance_status` (`COMPLIANT` / `NON_COMPLIANT`) and `violation_details` for each holding.
- Calculates overall portfolio compliance status.

### 3. Reporting
- Generates a compliance report summarizing portfolio pass/fail status.
- Includes per-holding findings and specific rule violations.
- Writes report output in human-readable form.
- Enables audit-friendly output saved to SQLite.

### 4. Persistence Layer
- Uses SQLite for storing portfolio holdings, rules, and reports.
- Ensures traceability for audit and historical review.
- Provides simple read/write operations for compliance records.

## SQLite Schema

### Table: `portfolio_holdings`
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

Indexes:
- `idx_portfolio_holdings_portfolio_id` on `portfolio_id`
- `idx_portfolio_holdings_ticker` on `ticker`

### Table: `compliance_rules`
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `rule_name` TEXT NOT NULL
- `rule_type` TEXT NOT NULL
- `threshold` REAL
- `parameters` TEXT
- `active` INTEGER

Indexes:
- `idx_compliance_rules_active` on `active`

### Table: `compliance_reports`
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `portfolio_id` TEXT NOT NULL
- `report_date` TEXT NOT NULL
- `overall_status` TEXT
- `summary` TEXT
- `created_at` TEXT

Indexes:
- `idx_compliance_reports_portfolio_id` on `portfolio_id`
- `idx_compliance_reports_report_date` on `report_date`

## Folder Structure

```
project-root/
  src/
    parser/
      csv_parser.py
      json_parser.py
      schema.py
    engine/
      compliance_engine.py
      rules.py
    reporting/
      report_generator.py
      templates.py
    persistence/
      sqlite_client.py
      repositories.py
    models/
      holding.py
      rule.py
      report.py
    cli.py
    app.py
  tests/
    test_parser.py
    test_engine.py
    test_reporting.py
    test_persistence.py
  data/
    sample_portfolios/
    sample_rules/
  _bmad-output/
    project-brief.md
    PRD.md
    architecture.md
  requirements.txt
  README.md
```

## Deployment Notes
- Keep the application lightweight and platform-independent using Python.
- Use SQLite for local persistence and audit trail support.
- Design the architecture so the parser, engine, and reporting modules are decoupled for future extension.
