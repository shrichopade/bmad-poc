import argparse
import csv
import json
import os
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

DB_FILENAME = "compliance.db"
REQUIRED_FIELDS = [
    "portfolio_id",
    "ticker",
    "asset_class",
    "quantity",
    "market_value",
    "country",
    "sector",
]

SAMPLE_RESTRICTED_STOCKS = [
    {"ticker": "ABC", "restriction_reason": "Insider trading restriction"},
    {"ticker": "XYZ", "restriction_reason": "Sanctioned issuer"},
]

SAMPLE_TRADES = [
    {
        "portfolio_id": "P-100",
        "ticker": "ABC",
        "asset_class": "Equity",
        "quantity": 100,
        "market_value": 15000,
        "country": "US",
        "sector": "Technology",
    },
    {
        "portfolio_id": "P-100",
        "ticker": "DEF",
        "asset_class": "Equity",
        "quantity": 200,
        "market_value": 52000,
        "country": "US",
        "sector": "Healthcare",
    },
    {
        "portfolio_id": "P-100",
        "ticker": "GHI",
        "asset_class": "Fixed Income",
        "quantity": 1000,
        "market_value": 25000,
        "country": "US",
        "sector": "Financials",
    },
]


def load_restricted_list(path: str) -> List[Dict[str, str]]:
    tickers = []
    with open(path, encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            ticker = raw_line.strip().upper()
            if not ticker:
                continue
            tickers.append({"ticker": ticker, "restriction_reason": f"Loaded from {os.path.basename(path)} (line {line_number})"})
    if not tickers:
        raise ValueError(f"Restricted list file '{path}' contains no ticker symbols.")
    return tickers


@dataclass
class Holding:
    portfolio_id: str
    ticker: str
    asset_class: str
    quantity: float
    market_value: float
    country: str
    sector: str
    compliance_status: str = "UNKNOWN"
    violation_details: str = ""
    evaluated_at: str = ""


@dataclass
class ComplianceReport:
    portfolio_id: str
    report_date: str
    overall_status: str
    summary: str
    created_at: str


class SQLiteClient:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolio_holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id TEXT NOT NULL,
                ticker TEXT NOT NULL,
                asset_class TEXT,
                quantity REAL,
                market_value REAL,
                country TEXT,
                sector TEXT,
                compliance_status TEXT,
                violation_details TEXT,
                evaluated_at TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS compliance_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT NOT NULL,
                rule_type TEXT NOT NULL,
                threshold REAL,
                parameters TEXT,
                active INTEGER
            )
            """
        )
        cursor.execute(
            """
            DELETE FROM compliance_rules
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM compliance_rules
                GROUP BY rule_type
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS compliance_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id TEXT NOT NULL,
                report_date TEXT NOT NULL,
                overall_status TEXT,
                summary TEXT,
                created_at TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS restricted_stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL UNIQUE,
                restriction_reason TEXT
            )
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_portfolio_id ON portfolio_holdings(portfolio_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_ticker ON portfolio_holdings(ticker)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_compliance_rules_active ON compliance_rules(active)")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_compliance_rules_rule_type_unique ON compliance_rules(rule_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_compliance_reports_portfolio_id ON compliance_reports(portfolio_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_compliance_reports_report_date ON compliance_reports(report_date)")
        self.connection.commit()

    def seed_restricted_stocks(self, restricted_stocks: List[Dict[str, str]]) -> None:
        cursor = self.connection.cursor()
        for stock in restricted_stocks:
            cursor.execute(
                "INSERT OR IGNORE INTO restricted_stocks (ticker, restriction_reason) VALUES (?, ?)",
                (stock["ticker"], stock["restriction_reason"]),
            )
        self.connection.commit()

    def seed_compliance_rules(self) -> None:
        cursor = self.connection.cursor()
        rules = [
            ("Restricted Stock Rule", "restricted_stock", None, None, 1),
            ("Maximum Position Value", "max_position_value", 50000.0, None, 1),
        ]
        for rule_name, rule_type, threshold, parameters, active in rules:
            cursor.execute(
                "INSERT INTO compliance_rules (rule_name, rule_type, threshold, parameters, active) VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(rule_type) DO UPDATE SET rule_name=excluded.rule_name, threshold=excluded.threshold, parameters=excluded.parameters, active=excluded.active",
                (rule_name, rule_type, threshold, parameters, active),
            )
        self.connection.commit()

    def fetch_restricted_tickers(self) -> Dict[str, str]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT ticker, restriction_reason FROM restricted_stocks")
        return {row["ticker"]: row["restriction_reason"] for row in cursor.fetchall()}

    def fetch_active_rules(self) -> List[Dict[str, Any]]:
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT DISTINCT rule_name, rule_type, threshold, parameters "
            "FROM compliance_rules WHERE active = 1"
        )
        return [dict(row) for row in cursor.fetchall()]

    def save_holding(self, holding: Holding) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO portfolio_holdings (
                portfolio_id,
                ticker,
                asset_class,
                quantity,
                market_value,
                country,
                sector,
                compliance_status,
                violation_details,
                evaluated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                holding.portfolio_id,
                holding.ticker,
                holding.asset_class,
                holding.quantity,
                holding.market_value,
                holding.country,
                holding.sector,
                holding.compliance_status,
                holding.violation_details,
                holding.evaluated_at,
            ),
        )
        self.connection.commit()

    def save_report(self, report: ComplianceReport) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO compliance_reports (
                portfolio_id,
                report_date,
                overall_status,
                summary,
                created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                report.portfolio_id,
                report.report_date,
                report.overall_status,
                report.summary,
                report.created_at,
            ),
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()


class PortfolioParser:
    @staticmethod
    def _validate_row(row: Dict[str, Any]) -> List[str]:
        missing = []
        for field in REQUIRED_FIELDS:
            if field not in row or row[field] == "":
                missing.append(field)
        return missing

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        if isinstance(value, str):
            text = value.strip()
            if text == "":
                return text
            try:
                if "." in text:
                    return float(text)
                return int(text)
            except ValueError:
                return text
        return value

    def load_csv(self, path: str) -> List[Holding]:
        with open(path, newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            holdings = []
            errors = []
            for line_number, raw_row in enumerate(reader, start=2):
                row = {k: self._normalize_value(v) for k, v in raw_row.items()}
                missing = self._validate_row(row)
                if missing:
                    errors.append(f"Line {line_number}: missing fields {missing}")
                    continue
                try:
                    holdings.append(self._build_holding(row))
                except ValueError as exc:
                    errors.append(f"Line {line_number}: {exc}")
            if errors:
                raise ValueError("CSV parse errors:\n" + "\n".join(errors))
            return holdings

    def load_json(self, path: str) -> List[Holding]:
        with open(path, encoding="utf-8") as json_file:
            data = json.load(json_file)
        if not isinstance(data, list):
            raise ValueError("JSON input must be an array of holdings")
        holdings = []
        errors = []
        for index, raw_row in enumerate(data, start=1):
            if not isinstance(raw_row, dict):
                errors.append(f"Item {index}: record must be a JSON object")
                continue
            row = {k: self._normalize_value(v) for k, v in raw_row.items()}
            missing = self._validate_row(row)
            if missing:
                errors.append(f"Item {index}: missing fields {missing}")
                continue
            try:
                holdings.append(self._build_holding(row))
            except ValueError as exc:
                errors.append(f"Item {index}: {exc}")
        if errors:
            raise ValueError("JSON parse errors:\n" + "\n".join(errors))
        return holdings

    def parse_trades(self, trades: Iterable[Dict[str, Any]]) -> List[Holding]:
        holdings = []
        errors = []
        for index, raw_row in enumerate(trades, start=1):
            row = {k: self._normalize_value(v) for k, v in raw_row.items()}
            missing = self._validate_row(row)
            if missing:
                errors.append(f"Trade {index}: missing fields {missing}")
                continue
            try:
                holdings.append(self._build_holding(row))
            except ValueError as exc:
                errors.append(f"Trade {index}: {exc}")
        if errors:
            raise ValueError("Trade parse errors:\n" + "\n".join(errors))
        return holdings

    @staticmethod
    def _build_holding(row: Dict[str, Any]) -> Holding:
        try:
            quantity = float(row["quantity"])
            market_value = float(row["market_value"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"numeric conversion failed: {exc}")
        return Holding(
            portfolio_id=str(row["portfolio_id"]),
            ticker=str(row["ticker"]).upper(),
            asset_class=str(row["asset_class"]),
            quantity=quantity,
            market_value=market_value,
            country=str(row["country"]),
            sector=str(row["sector"]),
        )


class ComplianceEngine:
    def __init__(self, db_client: SQLiteClient):
        self.db_client = db_client
        self.restricted_map = self.db_client.fetch_restricted_tickers()
        self.rules = self.db_client.fetch_active_rules()

    def evaluate(self, holdings: List[Holding]) -> List[Holding]:
        evaluated = []
        for holding in holdings:
            status, details = self._evaluate_holding(holding)
            holding.compliance_status = status
            holding.violation_details = details
            holding.evaluated_at = datetime.utcnow().isoformat()
            evaluated.append(holding)
        return evaluated

    def _evaluate_holding(self, holding: Holding) -> Tuple[str, str]:
        violations = []
        for rule in self.rules:
            if rule["rule_type"] == "restricted_stock":
                violation = self._check_restricted_stock(holding)
                if violation:
                    violations.append(violation)
            elif rule["rule_type"] == "max_position_value":
                violation = self._check_max_position_value(holding, rule["threshold"])
                if violation:
                    violations.append(violation)
        if violations:
            return "NON_COMPLIANT", "; ".join(violations)
        return "COMPLIANT", ""

    def _check_restricted_stock(self, holding: Holding) -> Optional[str]:
        reason = self.restricted_map.get(holding.ticker)
        if reason:
            return f"Restricted stock: {holding.ticker} ({reason})"
        return None

    @staticmethod
    def _check_max_position_value(holding: Holding, threshold: Optional[float]) -> Optional[str]:
        if threshold is None:
            return None
        if holding.market_value > float(threshold):
            return f"Position exceeds maximum allowed value ({holding.market_value} > {threshold})"
        return None


class ReportGenerator:
    @staticmethod
    def generate(holdings: List[Holding]) -> ComplianceReport:
        portfolio_id = holdings[0].portfolio_id if holdings else "UNKNOWN"
        non_compliant = [h for h in holdings if h.compliance_status == "NON_COMPLIANT"]
        overall_status = "NON_COMPLIANT" if non_compliant else "COMPLIANT"
        lines = [
            f"Portfolio ID: {portfolio_id}",
            f"Overall Status: {overall_status}",
            f"Evaluated Holdings: {len(holdings)}",
            "",
        ]
        for holding in holdings:
            lines.append(
                f"- {holding.ticker}: {holding.compliance_status}"
                + (f" | {holding.violation_details}" if holding.violation_details else "")
            )
        summary = "\n".join(lines)
        return ComplianceReport(
            portfolio_id=portfolio_id,
            report_date=datetime.utcnow().date().isoformat(),
            overall_status=overall_status,
            summary=summary,
            created_at=datetime.utcnow().isoformat(),
        )

    @staticmethod
    def print(report: ComplianceReport) -> None:
        print("=== Compliance Report ===")
        print(report.summary)
        print("=========================")


def get_db_path() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, DB_FILENAME)


def parse_command_line() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Portfolio Compliance Checker")
    parser.add_argument("--csv", help="Path to portfolio CSV file")
    parser.add_argument("--json", help="Path to portfolio JSON file")
    parser.add_argument(
        "--trades",
        help="Inline JSON array of trades to evaluate",
    )
    parser.add_argument(
        "--restricted",
        help="Path to restricted ticker list file",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Use built-in sample trades for a demonstration",
    )
    return parser.parse_args()


def load_holdings_from_args(parser: PortfolioParser, args: argparse.Namespace) -> List[Holding]:
    if args.csv:
        return parser.load_csv(args.csv)
    if args.json:
        return parser.load_json(args.json)
    if args.trades:
        try:
            trades = json.loads(args.trades)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Failed to parse trades JSON: {exc}")
        return parser.parse_trades(trades)
    if args.sample:
        return parser.parse_trades(SAMPLE_TRADES)
    raise ValueError("No input provided. Use --csv, --json, --trades, or --sample.")


def main() -> None:
    args = parse_command_line()
    db_client = SQLiteClient(get_db_path())
    try:
        restricted_stocks = SAMPLE_RESTRICTED_STOCKS
        if args.restricted:
            restricted_stocks = load_restricted_list(args.restricted)
        db_client.seed_restricted_stocks(restricted_stocks)
        db_client.seed_compliance_rules()
        parser = PortfolioParser()
        holdings = load_holdings_from_args(parser, args)
        engine = ComplianceEngine(db_client)
        evaluated_holdings = engine.evaluate(holdings)
        for holding in evaluated_holdings:
            db_client.save_holding(holding)
        report = ReportGenerator.generate(evaluated_holdings)
        db_client.save_report(report)
        ReportGenerator.print(report)
    except Exception as exc:
        print(f"Error: {exc}")
    finally:
        db_client.close()


if __name__ == "__main__":
    main()
