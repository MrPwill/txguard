# TxGuard AI — Agent Architecture
## Multi-Agent Investigation Crew Design

> This document details the CrewAI investigation layer. For how it integrates into the system lifecycle, see `Plan.md` (Phase 3) and `PRD.md` (FR-10 to FR-13). The async trigger flow connects to the Celery worker defined in `txguard-api/workers/celery_app.py`.

---

## Overview

When a transaction's risk score reaches ≥ 61 (HIGH or CRITICAL tier per `PRD.md` FR-06), TxGuard dispatches an autonomous investigation crew built on CrewAI. The crew operates as a sequential pipeline — each agent picks up where the last left off, building toward a final compliance-grade investigation report stored in the `InvestigationReport` table.

This design mirrors how a real compliance team works: a data analyst surfaces patterns, a fraud specialist identifies the scheme, a regulatory expert checks applicable law, and a senior officer makes the final call.

The crew must complete within **120 seconds** (hard timeout) per `PRD.md` FR-11 and NFR table.

---

## Crew Summary

```
Trigger: risk_score ≥ 61 (HIGH or CRITICAL)
         │
         ▼ Celery task: run_investigation.delay(alert_id)
         │
         ▼
┌──────────────────────────┐
│  Agent 1                 │
│  Transaction Analyst     │  ← Pulls transaction history, builds behavioral context
└──────────┬───────────────┘
           │ passes: BehavioralContext
           ▼
┌──────────────────────────┐
│  Agent 2                 │
│  Fraud Pattern           │
│  Investigator            │  ← Matches patterns against known fraud typologies
└──────────┬───────────────┘
           │ passes: PatternAssessment
           ▼
┌──────────────────────────┐
│  Agent 3                 │
│  Compliance &            │
│  Regulatory Specialist   │  ← Checks AML/KYC/FATF rules via RAG knowledge base
└──────────┬───────────────┘
           │ passes: RegulatoryAssessment
           ▼
┌──────────────────────────┐
│  Agent 4                 │
│  Risk Decision Officer   │  ← Synthesizes all inputs, writes final recommendation
└──────────┬───────────────┘
           │
           ▼
  InvestigationReport (persisted to PostgreSQL)
  WebSocket broadcast → WS /alerts/live
```

---

## Agent 1 — Transaction Analyst

**Role:** `Transaction Analyst`
**Goal:** Build a complete behavioral profile for the flagged account and transaction.

**Backstory:**
> You are a forensic data analyst specializing in financial transaction behavior. You have access to the account's full transaction history and real-time risk signals. Your job is to surface the behavioral facts — no interpretation, just clear, accurate context that the other investigators will rely on.

### Tools

| Tool | Description |
|---|---|
| `get_transaction_detail` | Fetches full transaction record from PostgreSQL by ID |
| `get_account_history` | Returns last 90 days of transactions for the account |
| `compute_velocity_stats` | Computes transaction counts across 1h, 6h, 24h, 7d windows |
| `get_geographic_profile` | Returns account's typical location countries and distance anomaly flag |
| `get_rule_trigger_detail` | Returns the rule flags fired and their raw input values |

### Output Schema

```json
{
  "account_id": "string",
  "transaction_summary": "string",
  "velocity_context": {
    "1h_count": "int",
    "24h_count": "int",
    "7d_avg_daily": "float"
  },
  "amount_context": {
    "transaction_amount": "float",
    "account_avg_amount": "float",
    "amount_z_score": "float"
  },
  "geographic_context": {
    "transaction_country": "string",
    "typical_countries": ["string"],
    "is_geographic_anomaly": "bool"
  },
  "rule_triggers": ["string"],
  "behavioral_anomaly_summary": "string"
}
```

---

## Agent 2 — Fraud Pattern Investigator

**Role:** `Fraud Pattern Investigator`
**Goal:** Match the behavioral context against known fraud and money laundering typologies to identify what type of scheme, if any, this transaction may represent.

**Backstory:**
> You are a fraud intelligence specialist with deep knowledge of financial crime patterns — card testing, structuring/smurfing, account takeover, mule account activity, and social engineering fraud. You receive behavioral data from the Transaction Analyst and determine which known typologies are consistent with what you're seeing.

### Tools

| Tool | Description |
|---|---|
| `search_fraud_typologies` | RAG search over curated fraud pattern library (card testing, structuring, ATO, mule accounts, layering) |
| `check_merchant_watchlist` | Looks up merchant name/MCC against internal and external risk lists |
| `get_counterparty_risk` | Checks if counterparty account has prior alerts or known risk associations |
| `compute_structuring_signals` | Detects patterns of transactions just below regulatory reporting thresholds |

### RAG Knowledge Base Sources

- FATF Typologies Reports (2020–2024)
- Egmont Group case studies
- FinCEN SAR activity reports
- Internal fraud pattern library (synthetic, curated for demo)

### Output Schema

```json
{
  "typology_matches": [
    {
      "typology_name": "string",
      "confidence": "float (0-1)",
      "matching_signals": ["string"],
      "source_citation": "string"
    }
  ],
  "structuring_detected": "bool",
  "counterparty_risk_level": "LOW | MEDIUM | HIGH | UNKNOWN",
  "merchant_risk_flags": ["string"],
  "pattern_assessment_summary": "string"
}
```

---

## Agent 3 — Compliance & Regulatory Specialist

**Role:** `AML Compliance Specialist`
**Goal:** Assess the transaction against applicable AML, KYC, and regulatory reporting obligations. Identify whether a Suspicious Activity Report (SAR) or Currency Transaction Report (CTR) threshold has been met.

**Backstory:**
> You are a compliance expert trained in AML regulations across multiple jurisdictions — FATF recommendations, the Bank Secrecy Act, EU AMLD6, and CBN AML/CFT regulations. You translate raw risk signals and fraud patterns into regulatory obligations. You cite specific rules and thresholds with precision.

### Tools

| Tool | Description |
|---|---|
| `search_aml_regulations` | RAG search over AML/CFT regulatory documents |
| `check_ctr_threshold` | Checks if amount triggers Currency Transaction Report ($10,000 USD equivalent) |
| `check_kyc_status` | Retrieves KYC verification status for the account |
| `search_sanctions_list` | Checks account and counterparty against OFAC SDN, UN, and EU sanctions lists |
| `get_jurisdiction_rules` | Returns relevant regulatory rules for the transaction's country |

### RAG Knowledge Base Sources

- FATF 40 Recommendations (2023 update)
- Bank Secrecy Act / FinCEN guidance
- EU AMLD6 key provisions
- CBN AML/CFT Regulations 2022 (Nigeria)
- OFAC compliance guidelines

### Output Schema

```json
{
  "sar_filing_indicated": "bool",
  "sar_reason": "string | null",
  "ctr_threshold_triggered": "bool",
  "sanctions_hit": "bool",
  "sanctions_details": "string | null",
  "kyc_status": "VERIFIED | PENDING | FAILED | UNKNOWN",
  "applicable_regulations": [
    {
      "regulation": "string",
      "relevant_provision": "string",
      "implication": "string"
    }
  ],
  "regulatory_assessment_summary": "string"
}
```

---

## Agent 4 — Risk Decision Officer

**Role:** `Chief Risk Decision Officer`
**Goal:** Synthesize all investigative findings into a final, auditable recommendation. This agent's output becomes the official `InvestigationReport` stored in PostgreSQL.

**Backstory:**
> You are a senior risk decision officer. You receive fully formed assessments from a behavioral analyst, a fraud investigator, and a compliance specialist. Your job is to weigh all inputs with clear logic, assign a confidence level to your conclusion, and produce a final recommendation that could withstand regulatory scrutiny. You write clearly, cite your reasoning, and never speculate beyond what the evidence supports.

### Tools

| Tool | Description |
|---|---|
| `get_similar_past_investigations` | RAG search over prior TxGuard investigation reports for precedent |
| `format_investigation_report` | Structured output formatter — maps agent output to the `InvestigationReport` DB schema |

### Output Schema

```json
{
  "recommended_action": "CLEAR | ESCALATE_TO_SAR | BLOCK_AND_HOLD | MONITOR",
  "confidence_score": "float (0-1)",
  "executive_summary": "string (2-3 sentences, regulator-facing)",
  "decision_rationale": "string (detailed reasoning)",
  "key_risk_factors": ["string"],
  "mitigating_factors": ["string"],
  "evidence_citations": [
    {
      "source": "string",
      "excerpt_summary": "string"
    }
  ],
  "next_actions": ["string"],
  "report_generated_at": "ISO8601"
}
```

---

## Crew Configuration (CrewAI)

```python
from crewai import Agent, Task, Crew, Process

crew = Crew(
    agents=[
        transaction_analyst,
        fraud_investigator,
        compliance_specialist,
        risk_decision_officer,
    ],
    tasks=[
        behavioral_analysis_task,
        pattern_investigation_task,
        regulatory_assessment_task,
        final_decision_task,
    ],
    process=Process.sequential,   # Agent 1 → 2 → 3 → 4
    memory=True,                  # Shared context across agents
    verbose=True,
    max_execution_time=120,       # Hard timeout: 120 seconds (per PRD NFR)
)
```

---

## RAG Architecture

```
ChromaDB (txguard-api/agents/rag/)
├── collection: fraud_typologies      ← FATF reports, Egmont case studies, FinCEN SARs
├── collection: aml_regulations       ← AML laws, CBN regs, FATF 40 Recs, AMLD6
├── collection: past_investigations   ← Prior TxGuard InvestigationReport records
└── collection: sanctions_data        ← OFAC SDN, UN, EU lists (sampled for demo)

Embedding model:  text-embedding-3-small (OpenAI) or all-MiniLM-L6-v2 (local fallback)
Chunking:         512 tokens, 64-token overlap
Retrieval:        top-k=5, MMR reranking
```

---

## Agent Tool Implementation Pattern

```python
from crewai_tools import tool
from api.models import Transaction
from api.dependencies import get_db

@tool("get_account_history")
def get_account_history(account_id: str) -> dict:
    """
    Returns the last 90 days of transactions for an account.
    Input: account_id (string)
    Output: list of transaction records with amounts, timestamps, merchants
    """
    db = next(get_db())
    ninety_days_ago = datetime.utcnow() - timedelta(days=90)
    transactions = (
        db.query(Transaction)
        .filter(Transaction.account_id == account_id)
        .filter(Transaction.timestamp >= ninety_days_ago)
        .order_by(Transaction.timestamp.desc())
        .all()
    )
    return {"transactions": [t.to_dict() for t in transactions]}
```

---

## Async Trigger Flow

```
1.  Hybrid scorer sets risk_score ≥ 61 → risk_tier = HIGH or CRITICAL
2.  Alert record created in PostgreSQL (investigation_status: PENDING)
3.  Celery task dispatched: run_investigation.delay(alert_id)
4.  Celery worker picks up task → Alert status updated to IN_PROGRESS
5.  CrewAI crew instantiated with alert_id and transaction context
6.  Agents run sequentially: Agent 1 → 2 → 3 → 4
7.  Agent 4 output mapped to InvestigationReport schema, written to PostgreSQL
8.  Alert investigation_status updated to COMPLETE
9.  WebSocket broadcast on WS /alerts/live: "investigation_complete:{alert_id}"
10. Frontend Investigation Report page (polling every 3s per PRD FR-23) receives update
    and renders the completed report
```

---

## Observability

Every agent action is logged to the `AuditLog` table with `action_type = AGENT_COMPLETED`, including:

- Agent name and task name
- Tools called (with inputs and outputs summarized)
- Token usage per agent
- Per-agent execution duration
- Total crew wall-clock time
- Final recommended action


The `agent_run_metadata` JSONB field in `InvestigationReport` stores the full per-agent trace, which is rendered as the Agent Chain component in the frontend Investigation Report page (`FRONTEND.md` §Investigation Report view).

## Coding standards

1. Use latest versions of libraries and idiomatic approaches as of today
2. Keep it simple - NEVER over-engineer, ALWAYS simplify, NO unnecessary defensive programming. No extra features - focus on simplicity.
3. README, IMPORTANT: no emojis ever
4. Principles of modularity must be adhered to- each file should be self-contained and easy to understand. Don't create unnecessary abstractions or layers of indirection.
5. Principles of clarity - always choose the most straightforward approach. Don't use clever tricks or obscure language features. Write code that is easy to read and understand.

6. The.env file in the root directory is where all the secrets are stored and .gitignore at the project root directory should be the only one and it must be updated to include .env file and all the other necessary and standard gitignores. There should be no .gitignore files in any other directories within the project structure.
7. Use uv as the package manager, always use uv commands to install packages and manage environments. 
8. Only one README.md file is allowed and it must be in the root directory.