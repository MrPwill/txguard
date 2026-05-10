# TxGuard AI — Project Plan
## Intelligent Transaction Monitoring & Fraud Investigation System

> **Why this project?**
> The Smartcomply JD asks for: anomaly detection, fraud/AML, rule-based + ML hybrid systems, FastAPI, LLMs/RAG (nice to have), and explainable AI. TxGuard hits every single one — and puts your agentic pipeline skills (CrewAI) front and center where most candidates only show notebooks.

---

## Project Summary

TxGuard AI is a production-grade transaction monitoring system that combines classical ML anomaly detection with a multi-agent LLM investigation layer. It ingests financial transactions, scores them in real-time, flags suspicious activity, deploys AI agents to autonomously investigate, and surfaces everything through a live compliance operations dashboard.

**The differentiator:** Most ML engineers build a model. You build an *intelligent system* — one that detects, explains, investigates, reports, and visualizes, end to end.

**Companion documents:**
- `PRD.md` — Full functional and non-functional requirements
- `AGENTS.md` — Multi-agent investigation crew architecture
- `FRONTEND.md` — Next.js dashboard design and technical spec

---

## Monorepo Structure

```text
Single Container Deployment:
- FastAPI
- Next.js
- Celery
- Nginx
- Supervisord

Managed Services:
- PostgreSQL
- Redis

txguard/
├── txguard-api/          # FastAPI backend
├── txguard-frontend/     # Next.js dashboard
├── infra/                # Terraform infrastructure
├── docker/               # Nginx and Supervisord configs
├── Dockerfile            # Unified container build
└── docker-compose.yml    # Local development orchestration
```

### Backend — `txguard-api/`

```
txguard-api/
├── api/
│   ├── main.py               # FastAPI app entrypoint
│   ├── routers/
│   │   ├── transactions.py   # Ingest, score, explain, audit endpoints
│   │   ├── alerts.py         # Alert queue + WebSocket feed
│   │   └── reports.py        # Investigation report retrieval
│   ├── models/               # SQLAlchemy ORM models
│   ├── schemas/              # Pydantic request/response schemas
│   └── dependencies.py       # DB session, auth, shared deps
├── ml/
│   ├── features.py           # Feature engineering pipeline
│   ├── train.py              # Model training scripts
│   ├── scorer.py             # Hybrid rule + ML scoring logic
│   ├── rules_engine.py       # Rule-based engine
│   ├── explainer.py          # SHAP explainability
│   └── drift_monitor.py      # Score distribution drift detection
├── agents/
│   ├── crew.py               # CrewAI crew definition (see AGENTS.md)
│   ├── tools/                # Agent tools (RAG lookup, DB query, sanctions check)
│   └── rag/                  # ChromaDB collections + document loaders
├── pipelines/
│   └── prefect_flows.py      # Batch pipeline DAGs (nightly retraining simulation)
├── workers/
│   └── celery_app.py         # Async investigation task definitions
├── data/
│   └── synthetic_gen.py      # Synthetic transaction dataset generator
├── Dockerfile
└── requirements.txt
```

### Frontend — `txguard-frontend/`

See `FRONTEND.md` for the full component tree and page architecture. Top-level:

```
txguard-frontend/
├── app/                      # Next.js App Router pages
├── components/               # UI component library
├── lib/                      # API client, Zustand stores, types
├── hooks/                    # Custom React hooks (WebSocket, queries)
├── public/
├── tailwind.config.ts
└── next.config.ts
```

---

## Full Tech Stack

### Backend

| Layer | Technology | Notes |
|---|---|---|
| API Framework | FastAPI | REST + SSE streaming + WebSocket |
| ML — Primary | Scikit-learn (Isolation Forest, LOF) | Anomaly detection core |
| ML — Optional | PyTorch autoencoder | Stretch goal |
| Rule Engine | Custom Python | Velocity, geo, blacklist, round-amount, off-hours |
| Agent Framework | CrewAI | 4-agent sequential investigation crew |
| LLM Provider | OpenRouter (Claude / GPT-4o) | Via OpenAI-compatible API |
| RAG | ChromaDB + LangChain | 4 collections — see AGENTS.md |
| Explainability | SHAP | Feature attribution per scoring decision |
| Database | PostgreSQL | Primary data store |
| Cache / Queue Broker | Redis | Velocity counters + Celery broker |
| Task Queue | Celery | Async investigation dispatch |
| Orchestration | Prefect | Batch pipeline DAGs |
| Containerization | Docker + Supervisord | Single Docker container deployment |
| Monitoring | Prometheus + Grafana | Stretch goal |

### Frontend

| Layer | Technology | Notes |
|---|---|---|
| Framework | Next.js 14 (App Router) | SSR + RSC for data fetching |
| Styling | Tailwind CSS + CSS Variables | Custom design tokens |
| Charts | Recharts | Area, Bar, Line charts |
| Real-time | TanStack Query + WebSocket | Polling + live alert feed |
| Global State | Zustand | Alert store, selected transaction |
| Tables | TanStack Table | Virtual scrolling for large datasets |
| Animations | Framer Motion | Staggered reveals, score ring transitions |
| HTTP Client | Axios | Typed, baseURL configured |
| Auth | NextAuth.js | Credentials provider for demo login |
| Deployment | Nginx | Served via static export in unified container |

---

## Build Phases

### Phase 1 — Data & ML Core (Week 1)
- [ ] Synthetic transaction dataset generation (amounts, merchants, geolocation, time patterns)
- [ ] Feature engineering pipeline (velocity, time-of-day, geo-distance, MCC encoding)
- [ ] Train Isolation Forest + Local Outlier Factor models
- [ ] Rule-based engine (velocity, blacklisted merchants, round-number, off-hours, cross-border)
- [ ] Hybrid scorer: merge rule flags + ML anomaly scores → unified risk score (0–100)
- [ ] Model serialization + versioning (joblib + metadata JSON)

### Phase 2 — FastAPI Backend (Week 1–2)
- [ ] All REST endpoints per PRD §6 API Surface
- [ ] SSE streaming on `POST /transactions/score`
- [ ] WebSocket on `WS /alerts/live`
- [ ] PostgreSQL models: Transaction, Alert, InvestigationReport, AuditLog
- [ ] Redis: velocity counter cache + Celery broker
- [ ] Celery worker: async investigation task trigger

### Phase 3 — Multi-Agent Investigation Layer (Week 2)
- [ ] CrewAI crew: 4-agent sequential pipeline (see AGENTS.md)
- [ ] RAG knowledge base: FATF, AML regs, sanctions data → ChromaDB
- [ ] SHAP explainer integrated into scoring response
- [ ] Agent output → structured InvestigationReport written to PostgreSQL
- [ ] Celery task wires alert → crew → report → WebSocket broadcast

### Phase 4 — Explainability & Auditability (Week 3)
- [ ] SHAP values on all ML predictions
- [ ] `GET /transactions/{id}/explain` returns full feature attribution
- [ ] Immutable AuditLog: every scoring event, rule trigger, agent action timestamped
- [ ] Human-readable risk reason codes (top 3 per transaction)

### Phase 5 — Frontend Dashboard (Week 3–4)
- [ ] Next.js project scaffold with Tailwind + design tokens
- [ ] Layout shell: sidebar, topbar, live status bar
- [ ] Overview page: KPI cards, volume chart, live alert feed, score distribution
- [ ] Transaction Monitor: searchable/filterable table with risk score cells
- [ ] Transaction Detail: hybrid score breakdown + SHAP chart + audit timeline
- [ ] Alert Queue: filterable by status, sortable, inline "Open Report"
- [ ] Investigation Report page: score ring, agent chain trace, recommendation banner, regulatory citations
- [ ] Model Health page: drift chart, feature importance, version table
- [ ] WebSocket integration: live alerts slide into feed in real time
- [ ] Connect all pages to FastAPI backend via React Query hooks

### Phase 6 — Productionization & Portfolio (Week 4)
- [ ] Docker Compose: Local development stack
- [ ] Prefect flow for nightly batch pipeline simulation
- [ ] Model drift detection wired to `/model/status` endpoint and frontend drift banner
- [ ] README: Excalidraw architecture diagram, setup guide, sample API calls
- [ ] Demo script: raw transaction → score → alert → investigation → report → dashboard
- [ ] Build unified Docker container
- [ ] Deploy container via Terraform to Cloud Run or Azure Container Apps

---

## Portfolio Presentation Strategy

1. **GitHub** — Clean monorepo with proper README, Excalidraw architecture diagram, CI badges. Pin `txguard` at the top of your profile.
2. **Hosted Demo** — Single container deployed via Terraform to Cloud Run or Azure Container Apps. Public Swagger UI at `/docs`. Enable "Demo Mode" on the dashboard (auto-fires a CRITICAL alert every 15s so the live feed is always active during review).
3. **Demo Video** — 3–5 min screen recording: ingest transactions → watch real-time score stream → alert fires → investigation runs → report appears → SHAP chart explains the decision. Record with the live feed running.
4. **Cover Email to Smartcomply** — Map each JD requirement to a specific TxGuard component:

| JD Requirement | TxGuard Component |
|---|---|
| Anomaly detection | Isolation Forest + LOF in `ml/scorer.py` |
| Rule-based + ML hybrid | `ml/rules_engine.py` + weighted hybrid formula |
| Fraud / AML | FATF typology RAG, SAR detection, sanctions check |
| FastAPI + REST/streaming | `api/` with SSE + WebSocket |
| LLMs / RAG (nice to have) | CrewAI crew + ChromaDB + OpenRouter |
| Explainable AI (XAI) | SHAP attribution + reason codes + audit log |
| Model drift monitoring | `ml/drift_monitor.py` + `/model/status` endpoint |
| Real-time systems | Celery async, Redis, WebSocket live feed |
| Frontend / ops visibility | Next.js dashboard — see FRONTEND.md |

---

## Success Metrics (What "Done" Looks Like)

| Metric | Target |
|---|---|
| Real-time scoring latency | < 200ms (p95) |
| Isolation Forest precision | > 85% on synthetic fraud set |
| Agent investigation time | < 120 seconds per alert |
| Docker container deployment | Single container deploys full application |
| Audit log coverage | 100% of scoring and agent decisions logged |
| Frontend initial page load | < 2s |
| Dashboard alert delivery | < 1s via WebSocket |
