#!/usr/bin/env python3
"""
TxGuard AI - End-to-End Demo Script
====================================
Demonstrates the full pipeline: transaction ingestion -> scoring ->
alert creation -> agent investigation -> investigation report.

Usage:
  python demo.py [--load-data] [--skip-agents]

Requirements:
  - Docker Compose running (postgres + redis)
  - DB seeded (--load-data to auto-load)
  - Optional: OPENROUTER_API_KEY for live agent investigation

Flags:
  --load-data     Seed the database with sample transactions first
  --skip-agents   Skip CrewAI agent investigation (faster demo, no LLM needed)
  --critical      Inject a CRITICAL-tier transaction for maximum drama
"""

import argparse
import json
import sys
import time
import uuid
import random
from datetime import datetime, timezone, timedelta

ENDPOINT = "http://localhost:8000/api/v1"


def print_step(n, title, color="cyan"):
    colors = {"cyan": "\033[96m", "yellow": "\033[93m", "green": "\033[92m",
              "red": "\033[91m", "magenta": "\033[95m", "bold": "\033[1m", "reset": "\033[0m"}
    print(f"\n{'='*60}")
    print(f"{colors.get(color, '')}{colors.get('bold', '')}STEP {n}: {title}{colors['reset']}")
    print(f"{'='*60}")


def load_data():
    print_step(0, "Loading Data into Database", "yellow")
    try:
        import requests
        resp = requests.post(
            f"{ENDPOINT}/transactions/ingest",
            json=[
                {
                    "id": f"DEMO-{i:04d}",
                    "account_id": f"ACC-{1000 + i}",
                    "amount": round(random.uniform(50, 15000), 2),
                    "currency": "USD",
                    "merchant_name": random.choice([
                        "TechMart Electronics", "Global Fuel Station", "Swift Transfer Co",
                        "City Grocers Ltd", "Amazon.com", "Crypto Exchange Inc", "Casino Royale"
                    ]),
                    "merchant_category_code": random.choice(["5411", "5541", "5732", "6012", "7995", "5814"]),
                    "timestamp": (datetime.now(timezone.utc) - timedelta(hours=random.randint(0, 72))).isoformat(),
                    "location_country": random.choice(["US", "GB", "NG", "DE", "CA"]),
                    "location_city": random.choice(["New York", "London", "Lagos", "Berlin", "Toronto"]),
                    "channel": random.choice(["online", "atm", "pos", "transfer"]),
                    "counterparty_account": random.choice([None, f"ACC-{random.randint(90000, 99999)}"])
                }
                for i in range(50)
            ],
            timeout=10
        )
        print(f"  Loaded {len(resp.json())} transactions into DB")
    except Exception as e:
        print(f"  Could not load data (is the API running?): {e}")


def ingest_transaction(is_critical=False):
    print_step(1, "Ingest Transaction", "cyan")

    if is_critical:
        txn = {
            "id": f"DEMO-CR-{uuid.uuid4().hex[:8].upper()}",
            "account_id": "ACC-99999",
            "amount": 20000.00,
            "currency": "USD",
            "merchant_name": "CRYPTO EXCHANGE INC",
            "merchant_category_code": "6012",
            "timestamp": datetime.now(timezone.utc).replace(hour=2).isoformat(),
            "location_country": "NG",
            "location_city": "Lagos",
            "channel": "online",
            "counterparty_account": "ACC-88888"
        }
    else:
        txn = {
            "id": f"DEMO-{uuid.uuid4().hex[:8].upper()}",
            "account_id": f"ACC-{random.randint(1000, 9999)}",
            "amount": round(random.uniform(5000, 12000), 2),
            "currency": "USD",
            "merchant_name": random.choice([
                "TechMart Electronics", "Global Fuel Station", "Swift Transfer Co",
                "City Grocers Ltd", "Casino Royale"
            ]),
            "merchant_category_code": random.choice(["5411", "5541", "5732", "6012", "7995"]),
            "timestamp": (datetime.now(timezone.utc) - timedelta(hours=random.randint(0, 24))).isoformat(),
            "location_country": random.choice(["US", "GB", "NG", "DE"]),
            "location_city": random.choice(["New York", "London", "Lagos", "Berlin"]),
            "channel": random.choice(["online", "pos", "transfer"]),
            "counterparty_account": f"ACC-{random.randint(90000, 99999)}"
        }

    print(f"  Transaction ID: {txn['id']}")
    print(f"  Account: {txn['account_id']} | Amount: ${txn['amount']:,.2f}")
    print(f"  Merchant: {txn['merchant_name']} (MCC: {txn['merchant_category_code']})")
    print(f"  Location: {txn['location_city']}, {txn['location_country']} | Time: {txn['timestamp']}")
    print(f"  Channel: {txn['channel']} | Counterparty: {txn.get('counterparty_account', 'None')}")

    try:
        import requests
        resp = requests.post(f"{ENDPOINT}/transactions/ingest", json=[txn], timeout=10)
        print(f"\n  Ingested: {resp.status_code == 200 or resp.status_code == 201}")
        return txn
    except Exception as e:
        print(f"  Error: {e}")
        return txn


def score_transaction(txn_id):
    print_step(2, "Score Transaction (Hybrid Rule + ML)", "cyan")

    try:
        import requests
        resp = requests.post(f"{ENDPOINT}/transactions/score?txn_id={txn_id}", timeout=30)
        result = resp.json()

        print(f"\n  Risk Score: {result.get('risk_score', 'N/A')}")
        print(f"  Risk Tier: {result.get('risk_tier', 'N/A')}")
        print(f"  ML Anomaly Score: {result.get('ml_anomaly_score', 'N/A')}")
        print(f"  Rule Triggers:")
        for trigger in (result.get('rule_triggers') or []):
            print(f"    - {trigger}")
        print(f"  Reason Codes: {result.get('reason_codes', [])}")

        return result
    except Exception as e:
        print(f"  Scoring error (API may not be running): {e}")
        return {"risk_tier": "HIGH", "risk_score": 75.0}


def check_alert(txn_id):
    print_step(3, "Check for Alert", "yellow")

    try:
        import requests
        resp = requests.get(f"{ENDPOINT}/alerts?transaction_id={txn_id}", timeout=10)
        alerts = resp.json()
        if alerts:
            alert = alerts[0]
            print(f"  Alert Created: YES")
            print(f"  Alert ID: {alert['id']}")
            print(f"  Risk Tier: {alert['risk_tier']}")
            print(f"  Investigation Status: {alert['investigation_status']}")
            return alert
        else:
            print("  Alert Created: NO (LOW/MEDIUM tier - auto-cleared)")
            return None
    except Exception as e:
        print(f"  Could not check alerts: {e}")
        return {"id": f"ALERT-DEMO-{uuid.uuid4().hex[:8].upper()}", "risk_tier": "HIGH", "investigation_status": "PENDING"}


def poll_investigation_report(txn_id, skip_agents=False, max_wait=30):
    print_step(4, "Agent Investigation (CrewAI)", "magenta")

    if skip_agents:
        print("  [SKIP-AGENTS MODE] Simulating investigation...")
        print("  Agent 1: Transaction Analyst - Building behavioral profile...")
        time.sleep(0.5)
        print("  Agent 2: Fraud Pattern Investigator - Matching typologies...")
        time.sleep(0.5)
        print("  Agent 3: AML Compliance Specialist - Checking regulatory obligations...")
        time.sleep(0.5)
        print("  Agent 4: Risk Decision Officer - Synthesizing recommendation...")
        time.sleep(0.5)
        print("  Investigation complete. Fetching report...")
        return get_report(txn_id)

    print("  Waiting for CrewAI investigation to complete...")
    print("  (Agents: Transaction Analyst -> Fraud Investigator -> Compliance Specialist -> Risk Officer)")
    print("  Watching for investigation_status = COMPLETE...")

    elapsed = 0
    while elapsed < max_wait:
        try:
            import requests
            resp = requests.get(f"{ENDPOINT}/transactions/{txn_id}/report", timeout=10)
            if resp.status_code == 200:
                report = resp.json()
                print(f"\n  Investigation Complete!")
                return report
        except Exception:
            pass
        time.sleep(2)
        elapsed += 2
        print(f"  ... waiting ({elapsed}s)")

    print("  Report not yet available (Celery worker may not be running).")
    return None


def get_report(txn_id):
    print_step(5, "Investigation Report", "green")

    mock_report = {
        "recommended_action": random.choice(["ESCALATE_TO_SAR", "BLOCK_AND_HOLD", "MONITOR"]),
        "confidence_score": round(random.uniform(0.75, 0.95), 2),
        "executive_summary": (
            "This transaction exhibits multiple high-risk indicators including large round amount "
            "($20,000), off-hours activity (02:00 local time), blacklisted merchant category (6012), "
            "and geographic anomaly (Nigeria from a US-typical account). Cross-border velocity "
            "and counterparty risk indicators further elevate the threat profile."
        ),
        "decision_rationale": (
            "The combination of blacklisted MCC code (6012 - Financial Institution), off-hours timing, "
            "and large round amount strongly suggests structuring or account compromise. The counterparty "
            "account shows no prior transaction history, increasing layering risk. AML regulations "
            "require CTR reporting for transactions exceeding $10,000."
        ),
        "key_risk_factors": [
            "Blacklisted merchant category (MCC 6012)",
            "Off-hours transaction at 02:00 local time",
            "Large round amount ($20,000) - potential structuring target",
            "Geographic anomaly: transaction from NG, account typically US-based",
            "High ML anomaly score (0.87)",
            "Counterparty account has no established history"
        ],
        "mitigating_factors": [
            "Account has prior good standing with 90-day history",
            "Single transaction (not part of clear structuring pattern yet)",
            "Amount below CTR threshold if reported in separate transactions"
        ],
        "evidence_citations": [
            {"source": "FATF Typology 2023", "excerpt": "Structuring involves breaking down large transactions to evade CTR reporting limits of $10,000."},
            {"source": "Bank Secrecy Act (BSA)", "excerpt": "All cash transactions exceeding $10,000 in a single business day must be reported."}
        ],
        "next_actions": [
            "File SAR if additional high-risk activity confirmed within 48 hours",
            "Place transaction on hold pending compliance review",
            "Notify account holder via secure channel",
            "Flag counterparty account for enhanced monitoring"
        ]
    }

    try:
        import requests
        resp = requests.get(f"{ENDPOINT}/transactions/{txn_id}/report", timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass

    return mock_report


def print_report(report):
    if not report:
        print("  No report available.")
        return

    tier_colors = {"ESCALATE_TO_SAR": "red", "BLOCK_AND_HOLD": "red", "MONITOR": "yellow", "CLEAR": "green"}
    color = tier_colors.get(report.get("recommended_action", "MONITOR"), "cyan")

    print(f"\n  RECOMMENDED ACTION: {report.get('recommended_action', 'N/A').replace('_', ' ')}")
    print(f"  Confidence Score: {report.get('confidence_score', 'N/A')}")
    print(f"\n  Executive Summary:")
    print(f"  {report.get('executive_summary', 'N/A')}")
    print(f"\n  Key Risk Factors:")
    for factor in (report.get("key_risk_factors") or []):
        print(f"    - {factor}")
    print(f"\n  Evidence Citations:")
    for citation in (report.get("evidence_citations") or []):
        print(f"    [{citation['source']}] {citation['excerpt'][:80]}...")
    print(f"\n  Next Actions:")
    for action in (report.get("next_actions") or []):
        print(f"    -> {action}")


def check_dashboard():
    print_step(6, "Dashboard", "cyan")
    print(f"  TxGuard Dashboard: http://localhost:3000/dashboard")
    print(f"  FastAPI Docs:       http://localhost:8000/docs")
    print(f"  WebSocket Feed:      ws://localhost:8000/alerts/live")
    print(f"\n  View the live alert feed at: http://localhost:3000/dashboard")
    print(f"  View investigation reports at: http://localhost:3000/dashboard/alerts")


def main():
    parser = argparse.ArgumentParser(description="TxGuard AI End-to-End Demo")
    parser.add_argument("--load-data", action="store_true", help="Seed database with sample transactions")
    parser.add_argument("--skip-agents", action="store_true", help="Skip CrewAI agent investigation")
    parser.add_argument("--critical", action="store_true", help="Inject a CRITICAL-tier transaction")
    args = parser.parse_args()

    banner = """
    ╔══════════════════════════════════════════════════════╗
    ║                   TxGuard AI Demo                    ║
    ║     Transaction Monitoring & Fraud Investigation      ║
    ╚══════════════════════════════════════════════════════╝
    """
    print(banner)

    if args.load_data:
        load_data()

    txn = ingest_transaction(is_critical=args.critical)
    result = score_transaction(txn["id"])
    alert = check_alert(txn["id"])

    if alert and result.get("risk_tier") in ["HIGH", "CRITICAL"]:
        report = poll_investigation_report(txn["id"], skip_agents=args.skip_agents)
        print_report(report)
    else:
        print_step(4, "No Agent Investigation", "yellow")
        print(f"  Transaction scored as {result.get('risk_tier', 'N/A')} - no investigation triggered.")

    check_dashboard()


if __name__ == "__main__":
    main()