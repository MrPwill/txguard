# TxGuard AI

Intelligent Transaction Monitoring & Fraud Investigation Platform

Real-time hybrid rule + ML risk scoring, autonomous multi-agent AI investigations via CrewAI, and a live compliance operations dashboard.

---

## Architecture

```
TxGuard AI Architecture
========================

  Client / Browser
        |
        | HTTPS / WebSocket
        v
  +---------------------------+
  |  Nginx (Port 8080)        |
  |  - Reverse proxy           |
  |  - Static asset serving    |
  +---------------------------+
        |
        +----------+------------------------+
        |          |                        |
        v          v                        v
  +-------------+  +------------------+  +----------------+
  | Next.js     |  | FastAPI Backend  |  | WebSocket      |
  | Dashboard   |  | (Port 8000)       |  | /alerts/live   |
  | (Port 3000) |  |                  |  +----------------+
  +-------------+  +------------------+
        |                  |
        |  API             |  REST + SSE
        |                  |
        v                  v
  +---------------------------+
  |  PostgreSQL (Port 5432)   |  <-- Transactions, Alerts,
  |  Redis (Port 6379)        |      InvestigationReports, AuditLogs
  +---------------------------+
        |        |
        v        v
  +--------------+  +------------------+
  | Celery Worker|  | ChromaDB RAG      |
  | (async tasks)|  | (vector store)    |
  +--------------+  +------------------+
        |
        v
  +----------------------+
  | CrewAI Agent Crew    |
  | (4-agent pipeline)   |
  +----------------------+
```

### Data Flow

```
Transaction Ingested
       |
       v
  [Rule Engine] ----> [Isolation Forest / LOF]
       |                        |
       | 0.4 weight             | 0.6 weight
       +-----------+------------+
                   v
           Final Risk Score (0-100)
                   |
       +-----------+-----------+
       |           |           |
    LOW (0-30) MEDIUM(31-60) HIGH (61-80) CRITICAL (81-100)
       |           |           |              |
    Auto-clear  Analyst    CrewAI Crew ----> Celery Task
                Queue        (async)       |
                                            v
                                      InvestigationReport
                                            |
                                            v
                                      WebSocket broadcast
                                            |
                                            v
                                      Dashboard Update
```

### Agent Crew Pipeline

```
Transaction Analyst --> Fraud Investigator --> Compliance Specialist --> Risk Officer
    (behavioral           (fraud patterns)       (AML/KYC/         (final recommendation)
     profile)                                       sanctions)
```


## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI (Python) |
| ML | Scikit-learn (Isolation Forest, LOF) |
| Rules | Custom Python rules engine |
| Agents | CrewAI (4-agent sequential pipeline) |
| LLM | OpenRouter (OpenAI-compatible) |
| RAG | ChromaDB |
| Explainability | SHAP |
| Database | PostgreSQL |
| Queue/Broker | Redis + Celery |
| Frontend | Next.js 14 (App Router) |
| Real-time | WebSocket + SSE |
| Container | Docker + Supervisord |
| Cloud | Google Cloud Run (Terraform) |

---

## Quick Start (Docker Compose)

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local dev without Docker)

### 1. Clone & Configure

```bash
git clone https://github.com/MrPwill/txguard.git
cd txguard
cp infra/terraform.tfvars.example infra/terraform.tfvars
```

### 2. Start Locally

```bash
# Start PostgreSQL + Redis + TxGuard (FastAPI + Celery + Nginx)
docker-compose up -d postgres redis

# Seed the database with sample transactions
docker-compose run --rm seed

# Start the main app
docker-compose up -d txguard
```

### 3. Access

| Service | URL |
|---|---|
| Dashboard | http://localhost:8080 |
| API Docs | http://localhost:8080/docs |
| OpenAPI Schema | http://localhost:8080/api/v1/openapi.json |
| WebSocket | ws://localhost:8080/alerts/live |

---

## API Reference

### Ingest Transactions

```bash
# Batch ingest (up to 500 per request)
curl -X POST http://localhost:8000/api/v1/transactions/ingest \
  -H "Content-Type: application/json" \
  -d '[
    {
      "account_id": "ACC-12345",
      "amount": 5000.00,
      "currency": "USD",
      "merchant_name": "TechMart Electronics",
      "merchant_category_code": "5732",
      "timestamp": "2026-05-10T14:30:00Z",
      "location_country": "US",
      "location_city": "New York",
      "channel": "online"
    }
  ]'
```

### Score a Transaction

```bash
# Synchronous scoring (returns full risk analysis)
curl -X POST "http://localhost:8000/api/v1/transactions/score?txn_id=TXN-10000"

# Streaming SSE (step-by-step: rules -> ML -> final)
curl -X GET "http://localhost:8000/api/v1/transactions/TXN-10000/score/stream"
```

### List Transactions

```bash
# All transactions
curl http://localhost:8000/api/v1/transactions

# Filter by risk tier
curl "http://localhost:8000/api/v1/transactions?tier=HIGH"

# Filter by account
curl "http://localhost:8000/api/v1/transactions?account_id=ACC-100000"
```

### Get Transaction Detail

```bash
# Basic details
curl http://localhost:8000/api/v1/transactions/TXN-10000

# SHAP feature attribution
curl http://localhost:8000/api/v1/transactions/TXN-10000/explain

# Audit trail
curl http://localhost:8000/api/v1/transactions/TXN-10000/audit

# Investigation report
curl http://localhost:8000/api/v1/transactions/TXN-10000/report
```

### Alerts

```bash
# List all alerts
curl http://localhost:8000/api/v1/alerts

# Filter by status
curl "http://localhost:8000/api/v1/alerts?status=COMPLETE"

# Filter by tier
curl "http://localhost:8000/api/v1/alerts?tier=CRITICAL"
```

### Model Health

```bash
# Check drift status, model versions, precision/recall
curl http://localhost:8000/api/v1/model/status
```

---

## Configuration

All configuration is via environment variables (`.env`):

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/txguard

# Redis (Celery broker)
REDIS_URL=redis://localhost:6379/0

# LLM for CrewAI agents
OPENROUTER_API_KEY=sk-or-v1-...

# ChromaDB vector store
CHROMA_PATH=./data/chroma_db

# ML model directory
MODEL_DIR=ml/saved_models

# Secrets
SECRET_KEY=your-secret-key
```

---

## Cloud Deployment (Google Cloud Run)

### 1. Build & Push Image

```bash
# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Build and push to Artifact Registry
./build.sh -p YOUR_PROJECT_ID -r us-central1 -t v1.0.0
```

### 2. Deploy with Terraform

```bash
cd infra
terraform init
terraform apply \
  -var="project_id=YOUR_PROJECT_ID" \
  -var="image=gcr.io/YOUR_PROJECT/txguard:v1.0.0" \
  -var="db_password=YOUR_STRONG_PASSWORD"
```

### 3. Post-Deploy

```bash
# Get the service URL
terraform output service_url

# View API docs
open "$(terraform output api_docs_url)"
```

The Terraform configuration creates:
- Cloud Run service (auto-scaling, VPC-connected)
- Cloud SQL PostgreSQL 16 (private networking)
- Memorystore Redis 7 (private connectivity)
- VPC network with private subnet
- Secret Manager for credentials
- Service account with minimal required roles

---

## Running the Demo

Once the application is running via Docker Compose, you can test the system:

```bash
# Ingest a test transaction
curl -X POST http://localhost:8000/api/v1/transactions/ingest \
  -H "Content-Type: application/json" \
  -d '[{
    "account_id": "ACC-TEST",
    "amount": 20000.00,
    "currency": "USD",
    "merchant_name": "Crypto Exchange",
    "merchant_category_code": "6012",
    "timestamp": "2026-05-11T02:00:00Z",
    "location_country": "NG",
    "location_city": "Lagos",
    "channel": "online"
  }]'

# Score the transaction to trigger a HIGH/CRITICAL alert
curl -X POST "http://localhost:8000/api/v1/transactions/score?txn_id=ACC-TEST"

# Check for alerts (should show HIGH or CRITICAL)
curl "http://localhost:8000/api/v1/alerts"

# View the investigation report (after Celery completes)
curl "http://localhost:8000/api/v1/transactions/ACC-TEST/report"
```

---

## Project Structure

```
txguard/
├── txguard-api/               # FastAPI backend
│   ├── api/
│   │   ├── main.py           # FastAPI app entrypoint
│   │   ├── routers/          # REST endpoints
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   └── dependencies.py    # Scorer, explainer, DB session
│   ├── ml/
│   │   ├── features.py       # Feature engineering
│   │   ├── scorer.py         # Hybrid rule + ML scorer
│   │   ├── rules_engine.py   # 6-rule fraud detection engine
│   │   ├── explainer.py      # SHAP feature attribution
│   │   └── saved_models/     # Trained Isolation Forest + LOF
│   ├── agents/
│   │   ├── crew.py           # 4-agent CrewAI pipeline
│   │   ├── tools/            # Agent tools (DB, RAG, compliance)
│   │   └── rag/              # ChromaDB collections
│   ├── workers/
│   │   └── celery_app.py     # Async investigation task
│   ├── pipelines/
│   │   └── prefect_flows.py  # Nightly batch pipeline
│   └── data/
│       ├── synthetic_gen.py  # Dataset generator
│       └── seed_transactions.py
├── txguard-frontend/          # Next.js 14 dashboard
│   ├── src/app/              # App Router pages
│   ├── src/components/       # UI components
│   └── src/lib/              # API client, stores, types
├── infra/                     # Terraform (GCP Cloud Run)
├── docker/                    # Nginx, Supervisord configs
├── docker-compose.yml         # Local development stack
├── Dockerfile                 # Unified container build
└── demo.py                    # End-to-end demo script
```

---

## Feature Summary

| Requirement | Implementation |
|---|---|
| Real-time scoring <200ms | Hybrid scorer with rule engine + ML |
| Anomaly detection | Isolation Forest + LOF on behavioral features |
| Explainability | SHAP feature attribution per transaction |
| Rule-based fraud detection | 6 configurable rules (velocity, geo, MCC, etc.) |
| Multi-agent investigation | 4-agent CrewAI crew with RAG knowledge base |
| Async Celery tasks | Investigation dispatched on HIGH/CRITICAL alerts |
| WebSocket real-time feed | Redis pub/sub to `WS /alerts/live` |
| SSE streaming | Step-by-step score stream on `/score/stream` |
| Immutable audit log | Every action timestamped to `AuditLog` table |
| Model drift monitoring | 7-day vs 14-day rolling mean comparison |
| SAR/CTR detection | Regulatory threshold checks via compliance agent |
| Sanctions screening | OFAC SDN checks via ChromaDB RAG |

---

## License

MIT