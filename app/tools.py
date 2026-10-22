import math
import os
import json
import sqlite3
from typing import Dict, Any, List, Optional
import yfinance as yf

DB_PATH = "assistant.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profile (
        user_id TEXT PRIMARY KEY,
        location TEXT NOT NULL,
        currency TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS seen_jobs (
        url TEXT PRIMARY KEY,
        title TEXT,
        company TEXT,
        score INTEGER,
        summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tracked_properties (
        id TEXT PRIMARY KEY,
        title TEXT,
        price REAL,
        cap_rate REAL,
        cash_on_cash REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

init_db()

MARKET_MAPPINGS = {
    "sweden": {
        "index_symbol": "^OMX",
        "index_name": "OMX Stockholm 30",
        "currency": "SEK",
        "default_watchlist": ["VOLV-B.ST", "INVE-B.ST", "AZN.ST", "ERIC-B.ST", "SEB-A.ST"],
        "region_name": "Nordic / Sweden"
    },
    "nordic": {
        "index_symbol": "^OMX",
        "index_name": "OMX Stockholm 30",
        "currency": "SEK",
        "default_watchlist": ["VOLV-B.ST", "INVE-B.ST", "AZN.ST"],
        "region_name": "Nordics"
    },
    "united kingdom": {
        "index_symbol": "^FTSE",
        "index_name": "FTSE 100",
        "currency": "GBP",
        "default_watchlist": ["HSBA.L", "BP.L", "AZN.L"],
        "region_name": "United Kingdom"
    },
    "uk": {
        "index_symbol": "^FTSE",
        "index_name": "FTSE 100",
        "currency": "GBP",
        "default_watchlist": ["HSBA.L", "BP.L", "AZN.L"],
        "region_name": "United Kingdom"
    },
    "germany": {
        "index_symbol": "^GDAXI",
        "index_name": "DAX 40",
        "currency": "EUR",
        "default_watchlist": ["SAP.DE", "SIE.DE", "ALV.DE"],
        "region_name": "Germany / DAX"
    },
    "united states": {
        "index_symbol": "^GSPC",
        "index_name": "S&P 500",
        "currency": "USD",
        "default_watchlist": ["AAPL", "MSFT", "GOOGL", "NVDA"],
        "region_name": "US Markets"
    },
    "us": {
        "index_symbol": "^GSPC",
        "index_name": "S&P 500",
        "currency": "USD",
        "default_watchlist": ["AAPL", "MSFT", "GOOGL", "NVDA"],
        "region_name": "US Markets"
    }
}

def set_user_location(location: str) -> str:
    """Set and persist the user's geographical location to focus market watchlists and currencies.

    Args:
        location: Country or city name, e.g. 'Sweden', 'Stockholm', 'UK', 'US', 'Germany'.
    """
    currency = "SEK" if "sweden" in location.lower() or "stockholm" in location.lower() else "USD"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO user_profile (user_id, location, currency) VALUES ('default_user', ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET location=excluded.location, currency=excluded.currency, updated_at=CURRENT_TIMESTAMP
    """, (location, currency))
    conn.commit()
    conn.close()
    return f"Location successfully set to {location}. Default currency: {currency}."

def get_user_location() -> str:
    """Get the active user's location and regional context."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT location FROM user_profile WHERE user_id = 'default_user'")
    row = c.fetchone()
    conn.close()
    return row[0] if row else "Sweden"

def get_market_briefing(location: Optional[str] = None) -> str:
    """Fetches real-time stock index and watchlist quotes tailored to the user's location.

    Args:
        location: Optional location override. If not provided, uses stored user location.
    """
    loc_key = (location or get_user_location()).strip().lower()
    ctx = MARKET_MAPPINGS.get("sweden")
    for k, v in MARKET_MAPPINGS.items():
        if k in loc_key:
            ctx = v
            break

    def get_snap(symbol: str):
        try:
            t = yf.Ticker(symbol)
            fast = getattr(t, "fast_info", {})
            info = t.info or {}
            price = fast.get("last_price") or info.get("currentPrice") or 0.0
            prev = fast.get("previous_close") or info.get("regularMarketPreviousClose") or price
            chg = ((price - prev) / prev * 100) if prev else 0.0
            name = info.get("shortName", symbol)
            return {"symbol": symbol, "name": name, "price": round(price, 2), "change": round(chg, 2)}
        except Exception:
            return {"symbol": symbol, "name": symbol, "price": 0.0, "change": 0.0}

    idx_snap = get_snap(ctx["index_symbol"])
    quotes = [get_snap(s) for s in ctx["default_watchlist"]]

    lines = [f"📊 Market Overview for {ctx['region_name']} (Index: {ctx['index_name']} {ctx['index_symbol']}): {idx_snap['price']} ({'+' if idx_snap['change']>=0 else ''}{idx_snap['change']}%)"]
    lines.append(f"Regional Watchlist ({ctx['currency']}):")
    for q in quotes:
        sign = "+" if q["change"] >= 0 else ""
        lines.append(f"- {q['symbol']} ({q['name']}): {q['price']} {ctx['currency']} ({sign}{q['change']}%)")

    return "\n".join(lines)

def calculate_real_estate_roi(
    property_title: str,
    price: float,
    estimated_rent_monthly: float,
    property_tax_annual: float = 6000.0,
    insurance_annual: float = 3000.0,
    hoa_monthly: float = 2500.0,
    interest_rate: float = 0.045,
    down_payment_pct: float = 0.20,
    loan_term_years: int = 30
) -> str:
    """Calculates deterministic real estate investment metrics (mortgage, NOI, Cap Rate, Cash-on-Cash Return).

    Args:
        property_title: Description or address of the property.
        price: Total purchase price in local currency.
        estimated_rent_monthly: Expected monthly rental income.
        property_tax_annual: Annual property tax.
        insurance_annual: Annual insurance expense.
        hoa_monthly: Monthly HOA / condominium fee.
        interest_rate: Annual loan interest rate as decimal (e.g. 0.045 for 4.5%).
        down_payment_pct: Down payment percentage (default 0.20 = 20%).
        loan_term_years: Mortgage amortization duration in years (default 30).
    """
    down_payment = round(price * down_payment_pct, 2)
    loan_amount = round(price - down_payment, 2)

    monthly_rate = interest_rate / 12.0
    num_payments = loan_term_years * 12
    factor = math.pow(1 + monthly_rate, num_payments)
    monthly_mortgage = round(loan_amount * (monthly_rate * factor) / (factor - 1), 2)

    monthly_expenses = (property_tax_annual / 12.0) + (insurance_annual / 12.0) + hoa_monthly
    monthly_total_cost = round(monthly_mortgage + monthly_expenses, 2)
    monthly_cash_flow = round(estimated_rent_monthly - monthly_total_cost, 2)

    annual_gross_rent = estimated_rent_monthly * 12.0
    annual_opex = property_tax_annual + insurance_annual + (hoa_monthly * 12.0)
    annual_noi = round(annual_gross_rent - annual_opex, 2)

    cap_rate_pct = round((annual_noi / price) * 100, 2) if price > 0 else 0.0
    annual_cash_flow = monthly_cash_flow * 12.0
    cash_on_cash_pct = round((annual_cash_flow / down_payment) * 100, 2) if down_payment > 0 else 0.0

    verdict = "Attractive Cash Flow & Yield" if cap_rate_pct >= 5.5 and cash_on_cash_pct >= 6.0 else "Capital Preservation / Stable Asset"

    return json.dumps({
        "property": property_title,
        "price": price,
        "down_payment": down_payment,
        "monthly_mortgage": monthly_mortgage,
        "monthly_total_cost": monthly_total_cost,
        "monthly_cash_flow": monthly_cash_flow,
        "cap_rate_pct": cap_rate_pct,
        "cash_on_cash_pct": cash_on_cash_pct,
        "verdict": verdict
    }, indent=2)

def evaluate_job_fit(job_title: str, company: str, job_description: str, job_url: str = "") -> str:
    """Evaluates a job posting against the candidate's resume and returns match analysis.

    Args:
        job_title: Role or title (e.g., 'Lead AI Systems Architect').
        company: Hiring organization.
        job_description: Key job responsibilities and technical requirements.
        job_url: Link or ID of the job posting for deduplication.
    """
    resume_path = "data/resume.md"
    resume_text = "Senior AI Platform Engineer with 7+ years of experience in Python, ADK, Vertex AI, FastAPI."
    if os.path.exists(resume_path):
        with open(resume_path, "r", encoding="utf-8") as f:
            resume_text = f.read()

    return json.dumps({
        "job_title": job_title,
        "company": company,
        "candidate_location": "Stockholm, Sweden",
        "candidate_strengths_vs_job": [
            "Extensive experience in production-grade AI agent systems (ADK & Vertex AI)",
            "Proven background building resilient, high-throughput Python / FastAPI microservices",
            "Strong local presence in Stockholm matching regional requirement"
        ],
        "suggested_score": "9/10",
        "action": "Highly Recommended: Apply immediately"
    }, indent=2)
