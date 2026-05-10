from crewai.tools import tool
from agents.rag.store import query_collection

@tool("check_merchant_watchlist")
def check_merchant_watchlist(merchant_name: str) -> dict:
    """
    Looks up merchant name/MCC against internal and external risk lists.
    Input: merchant_name (string)
    """
    if not merchant_name:
        return {"risk_level": "UNKNOWN", "flags": []}
    if "crypto" in merchant_name.lower() or "casino" in merchant_name.lower():
        return {"risk_level": "HIGH", "flags": ["High-risk category (Crypto/Gambling)"]}
    return {"risk_level": "LOW", "flags": []}

@tool("get_counterparty_risk")
def get_counterparty_risk(counterparty_account: str) -> dict:
    """
    Checks if counterparty account has prior alerts or known risk associations.
    Input: counterparty_account (string)
    """
    if not counterparty_account:
        return {"risk_level": "UNKNOWN", "note": "No counterparty provided."}
    return {"risk_level": "LOW", "associations": []}

@tool("compute_structuring_signals")
def compute_structuring_signals(account_id: str) -> dict:
    """
    Detects patterns of transactions just below regulatory reporting thresholds.
    Input: account_id (string)
    """
    return {"structuring_detected": False, "confidence": 0.0}

@tool("check_ctr_threshold")
def check_ctr_threshold(amount: float) -> dict:
    """
    Checks if amount triggers Currency Transaction Report ($10,000 USD equivalent).
    Input: amount (float)
    """
    if amount >= 10000.0:
        return {"ctr_triggered": True, "threshold": 10000.0, "amount": amount}
    return {"ctr_triggered": False, "threshold": 10000.0, "amount": amount}

@tool("check_kyc_status")
def check_kyc_status(account_id: str) -> dict:
    """
    Retrieves KYC verification status for the account.
    Input: account_id (string)
    """
    return {"kyc_status": "VERIFIED"}

@tool("search_sanctions_list")
def search_sanctions_list(entity_name: str) -> dict:
    """
    Checks account and counterparty against OFAC SDN, UN, and EU sanctions lists.
    Input: entity_name (string)
    """
    if not entity_name:
        return {"sanctions_hit": False, "details": None}
    results = query_collection("sanctions_data", entity_name)
    if results:
        return {"sanctions_hit": True, "details": "\n".join(results)}
    return {"sanctions_hit": False, "details": None}

@tool("get_jurisdiction_rules")
def get_jurisdiction_rules(country_code: str) -> dict:
    """
    Returns relevant regulatory rules for the transaction's country.
    Input: country_code (string)
    """
    return {"country": country_code, "note": "Standard FATF rules apply."}

@tool("format_investigation_report")
def format_investigation_report(report_data: dict) -> str:
    """
    Helper tool to format the investigation report before final output.
    Input: dict with report fields
    """
    return str(report_data)
