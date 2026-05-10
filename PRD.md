# TxGuard AI — Product Requirements Document (PRD)
**Version:** 1.0
**Author:** Princewill
**Status:** Active
**Last Updated:** May 2026

> This document covers the full system requirements — backend API, ML pipeline, agent layer, and frontend dashboard. For architectural detail on specific layers, see `Plan.md` (build roadmap), `AGENTS.md` (agent crew design), and `FRONTEND.md` (dashboard spec).

---

## 1. Overview

### 1.1 Product Vision

TxGuard AI is an intelligent transaction monitoring and fraud investigation platform that provides real-time risk scoring, automated behavioral anomaly detection, LLM-powered compliance reporting, and a live operations dashboard — built to the production standards expected in regulated fintech and compliance environments.

### 1.2 Problem Statement

Compliance and fraud operations teams face two compounding challenges:

- **Volume:** Modern payment systems process thousands of transactions per second — human review cannot scale.
- **Explainability:** Regulators (FATF, CBN, FCA) require that flagged transactions come with auditable, human-readable justifications — a black-box model score is insufficient for compliance.

Existing solutions are either pure rule-engines (brittle, easy to game) or pure ML models (opaque, difficult to audit). TxGuard bridges this gap with a hybrid rule + ML scoring layer, an autonomous AI investigation crew that produces compliance-grade reports, and a real-time dashboard that makes every decision visible.

### 1.3 Target Users (Simulated)

| User | Need |
|---|---|
| Compliance Analyst | Review flagged transactions with full investigation context via the dashboard |
| Risk Manager | Monitor system health, score distributions, and drift signals |
| Regulator / Auditor | Access the complete, immutable audit trail for any flagged transaction |

---

## 2. Goals & Non-Goals

### Goals

- Ingest transactions (batch and real-time) and produce a hybrid risk score in < 200ms
- Automatically trigger multi-agent investigation for HIGH and CRITICAL alerts
- Produce structured, human-readable investigation reports with regulatory citations
- Maintain a complete, immutable audit log of all system decisions
- Expose all functionality through a documented REST + streaming API
- Surface all system data through a real-time Next.js compliance operations dashboard

### Non-Goals

- This is not a payment processing system (no card rails, no fund movement)
- This does not replace human compliance review — it augments it
- Live integration with real banking APIs is out of scope (synthetic data only for portfolio demo)

---

## 3. Functional Requirements

### 3.1 Transaction Ingestion

**FR-01:** The system shall accept transaction payloads via `POST /transactions/ingest` (batch, up to 500 per request).

**FR-02:** Each transaction record shall contain:
```json
{
  "transaction_id": "uuid",
  "account_id": "string",
  "amount": "float",
  "currency": "string",
  "merchant_name": "string",
  "merchant_category_code": "string",
  "timestamp": "ISO8601",
  "location_country": "string",
  "location_city": "string",
  "channel": "online | atm | pos | transfer",
  "counterparty_account": "string | null"
}
```

**FR-03:** Transactions shall be persisted to PostgreSQL on ingestion with status `PENDING`.

---

### 3.2 Hybrid Risk Scoring

**FR-04:** The system shall score every ingested transaction through a two-layer hybrid engine:

**Layer 1 — Rule Engine:**

| Rule | Trigger Condition | Flag Weight |
|---|---|---|
| High Velocity | > 5 transactions in 60 minutes from same account | +30 |
| Large Round Amount | Amount is a round number > $5,000 | +15 |
| Geographic Anomaly | Country differs from account's last 10 transactions | +25 |
| Blacklisted Merchant | Merchant MCC matches internal watchlist | +40 |
| Off-Hours Transaction | Timestamp between 01:00–04:00 local time | +10 |
| Rapid Cross-Border | > 2 countries in 24 hours | +35 |

**Layer 2 — ML Anomaly Detection:**
- Primary model: Isolation Forest trained on behavioral features
- Secondary model: Local Outlier Factor for neighborhood-based anomaly detection
- Features: transaction amount z-score, velocity score, time-of-day encoding, merchant category encoding, geographic distance from median location
- Output: anomaly score normalized 0–1

**FR-05:** Final Risk Score = `(Rule Weight Sum × 0.4) + (ML Anomaly Score × 100 × 0.6)`, clamped to 0–100.

**FR-06:** Risk tiers shall be:

| Score Range | Tier | Automated Action |
|---|---|---|
| 0–30 | LOW | Auto-clear, log only |
| 31–60 | MEDIUM | Flag for analyst queue |
| 61–80 | HIGH | Trigger async agent investigation |
| 81–100 | CRITICAL | Trigger urgent agent investigation + block simulation |

**FR-07:** Scoring response shall include: `risk_score`, `risk_tier`, `rule_triggers[]`, `ml_anomaly_score`, `reason_codes[]` (top 3, human-readable), `scored_at`.

---

### 3.3 Real-Time Streaming

**FR-08:** `POST /transactions/score` shall support server-sent events (SSE), streaming partial results in order: rule evaluation → ML score → final tier → reason codes.

**FR-09:** `WS /alerts/live` shall push new HIGH and CRITICAL alert payloads to all connected clients in real time, within 1 second of alert creation.

---

### 3.4 Multi-Agent Investigation

**FR-10:** For every HIGH or CRITICAL alert (risk score ≥ 61), the system shall asynchronously dispatch a CrewAI investigation crew via Celery. See `AGENTS.md` for the full crew design.

**FR-11:** Investigation shall complete within 120 seconds and produce a structured report containing:
- Transaction summary and risk factors
- Behavioral pattern analysis (account history context)
- Fraud typology assessment with FATF source citations
- Regulatory assessment (AML/KYC flags, SAR/CTR thresholds, sanctions check)
- Recommended action: `CLEAR | ESCALATE_TO_SAR | BLOCK_AND_HOLD | MONITOR`
- Confidence score (0–1) for the recommendation
- Supporting evidence citations from RAG knowledge base

**FR-12:** Investigation reports shall be persisted to the `InvestigationReport` table and retrievable via `GET /transactions/{id}/report`.

**FR-13:** On investigation completion, the system shall broadcast a WebSocket event to `WS /alerts/live` notifying connected clients that the report is ready.

---

### 3.5 Explainability

**FR-14:** `GET /transactions/{id}/explain` shall return SHAP feature attribution values for the ML model's scoring decision, including per-feature contribution scores and direction (positive/negative).

**FR-15:** Every scoring response (FR-07) shall include `reason_codes[]` — a maximum of 3 human-readable strings derived from the top contributing rule triggers and SHAP features (e.g. `"High velocity: 7 transactions in 60 minutes"`, `"Geographic anomaly: new country NG"`).

---

### 3.6 Audit & Compliance

**FR-16:** Every system action shall be written to an immutable `AuditLog` table, covering: ingestion, rule evaluation, ML scoring, alert creation, Celery task dispatch, agent task completion, and report generation.

**FR-17:** Audit entries shall be queryable by `transaction_id`, `account_id`, `timestamp range`, and `action_type`.

**FR-18:** `GET /transactions/{id}/audit` shall return the complete, ordered decision chain for any transaction.

---

### 3.7 Model Lifecycle

**FR-19:** Trained models shall be serialized with metadata: version, training date, feature list, training set size, precision and recall on validation set.

**FR-20:** The system shall monitor score distribution daily and emit a drift alert if the mean risk score shifts > 15% from the 7-day rolling baseline. Drift status shall be exposed via `GET /model/status` and reflected in the frontend Model Health page.

---

### 3.8 Frontend Dashboard

**FR-21:** A Next.js dashboard shall consume all backend APIs and provide the following views. See `FRONTEND.md` for full component and interaction specs.

| View | Path | Purpose |
|---|---|---|
| Overview | `/dashboard` | KPI cards, 24h volume chart, live alert feed, risk distribution |
| Transaction Monitor | `/dashboard/transactions` | Searchable, filterable transaction table with risk scores |
| Transaction Detail | `/dashboard/transactions/[id]` | Score breakdown, SHAP chart, audit timeline |
| Alert Queue | `/dashboard/alerts` | HIGH/CRITICAL alerts with status, sortable and filterable |
| Investigation Report | `/dashboard/alerts/[id]` | Full agent report: chain trace, recommendation, regulatory citations |
| Model Health | `/dashboard/model` | Drift chart, feature importance, model version table |

**FR-22:** The live alert feed on the Overview and Alert Queue pages shall receive new alerts via WebSocket (`WS /alerts/live`) with < 1 second delivery latency, consistent with FR-09.

**FR-23:** The Investigation Report page shall poll `GET /transactions/{id}/report` every 3 seconds while `investigation_status = IN_PROGRESS` and render the completed report upon receipt, surfacing the agent chain with per-agent execution times.

---

## 4. Non-Functional Requirements

| Requirement | Target |
|---|---|
| Scoring latency (p95) | < 200ms |
| Alert WebSocket delivery | < 1 second |
| Investigation completion | < 120 seconds |
| API availability | > 99.5% (local demo) |
| Audit log retention | All records (no TTL in demo) |
| API documentation | Full OpenAPI spec auto-generated at `/docs` |
| Containerization | Single Docker container deploys the entire application stack |
| Frontend initial load | < 2 seconds |
| Frontend navigation | < 500ms between pages |

---

## 5. Data Model

```
Transaction
  id                  uuid, PK
  account_id          string, indexed
  amount              float
  currency            string
  merchant_name       string
  merchant_category_code string
  channel             enum: online | atm | pos | transfer
  location_country    string
  location_city       string
  counterparty_account string | null
  timestamp           timestamptz
  status              enum: PENDING | SCORED | FLAGGED | CLEARED | BLOCKED
  risk_score          float
  risk_tier           enum: LOW | MEDIUM | HIGH | CRITICAL
  reason_codes        JSONB
  created_at          timestamptz
  updated_at          timestamptz

Alert
  id                  uuid, PK
  transaction_id      FK → Transaction
  risk_tier           enum: HIGH | CRITICAL
  rule_triggers       JSONB
  ml_anomaly_score    float
  reason_codes        JSONB
  investigation_status enum: PENDING | IN_PROGRESS | COMPLETE | ESCALATED
  created_at          timestamptz

InvestigationReport
  id                  uuid, PK
  alert_id            FK → Alert
  transaction_id      FK → Transaction
  behavioral_analysis text
  typology_assessment JSONB
  regulatory_assessment text
  recommended_action  enum: CLEAR | ESCALATE_TO_SAR | BLOCK_AND_HOLD | MONITOR
  confidence_score    float
  evidence_citations  JSONB
  agent_run_metadata  JSONB          ← per-agent name, duration, token usage
  generated_at        timestamptz

AuditLog
  id                  uuid, PK
  transaction_id      string, indexed
  action_type         enum: INGESTED | RULE_EVALUATED | ML_SCORED | ALERT_CREATED |
                            INVESTIGATION_DISPATCHED | AGENT_COMPLETED | REPORT_WRITTEN
  actor               string         ← "system" | agent name
  payload             JSONB
  timestamp           timestamptz
```

---

## 6. API Surface

| Method | Endpoint | Description |
|---|---|---|
| POST | `/transactions/ingest` | Batch transaction ingestion (up to 500) |
| POST | `/transactions/score` | Real-time single-transaction score (SSE streaming) |
| GET | `/transactions/{id}` | Transaction detail |
| GET | `/transactions/{id}/explain` | SHAP feature attribution |
| GET | `/transactions/{id}/report` | Investigation report |
| GET | `/transactions/{id}/audit` | Full ordered audit chain |
| GET | `/alerts` | Paginated alert list (filter by tier, status) |
| WS | `/alerts/live` | Real-time WebSocket alert feed |
| GET | `/model/status` | Model versions, drift status, feature importance |
| GET | `/health` | System health check |

---

## 7. Milestones

| Milestone | Deliverable | Phase | Target |
|---|---|---|---|
| M1 | ML models trained, hybrid scorer working | Phase 1 | End of Week 1 |
| M2 | FastAPI backend with all REST + WS endpoints | Phase 2 | End of Week 2 |
| M3 | Agent crew integrated, producing reports via Celery | Phase 3 | End of Week 2 |
| M4 | SHAP explainability + immutable audit log complete | Phase 4 | Mid Week 3 |
| M5 | Next.js dashboard — all views wired to live backend | Phase 5 | End of Week 4 |
| M6 | Single Docker container, drift monitor, README | Phase 6 | End of Week 4 |
| M7 | Terraform deployment + demo video + portfolio packaging | Phase 6 | End of Week 4 |
