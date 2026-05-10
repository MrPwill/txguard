# TxGuard AI — Technical Walkthrough

TxGuard AI is an intelligent, production-grade transaction monitoring and fraud investigation platform. It bridges the gap between brittle rule-based systems and opaque machine learning models by using a **hybrid scoring engine** and **autonomous AI agents** to provide explainable, compliance-ready fraud detection.

---

## 1. System Architecture

The project follows a modern, distributed architecture:

- **Frontend:** Next.js 14 dashboard providing real-time visibility into transactions and alerts.
- **Backend API:** FastAPI service for high-performance ingestion, scoring, and data retrieval.
- **ML Layer:** Scikit-learn models (Isolation Forest) providing behavioral anomaly detection.
- **Agent Layer:** CrewAI multi-agent crew for autonomous investigation of high-risk flags.
- **Task Queue:** Celery + Redis for asynchronous agent orchestration.
- **Persistence:** PostgreSQL for transactional data and ChromaDB for RAG-based compliance knowledge.

---

## 2. Core Components & Logic

### 2.1 Hybrid Risk Scoring (`txguard-api/ml/scorer.py`)
Every transaction is scored using a weighted hybrid formula:
- **Rule Engine (40% weight):** Evaluates hard-coded compliance rules like velocity (too many txns in 1 hour), geographic anomalies, and blacklisted merchants.
- **ML Layer (60% weight):** Uses an **Isolation Forest** model to detect outliers in behavioral features (amount, time, category).
- **Final Score (0-100):** Transactions scoring > 60 are flagged as HIGH/CRITICAL and trigger an investigation.

### 2.2 Multi-Agent Investigation (`txguard-api/agents/crew.py`)
When a high-risk alert is fired, a **CrewAI** crew of 4 specialized agents is deployed:
1.  **Transaction Analyst:** Builds a behavioral profile from historical data.
2.  **Fraud Investigator:** Matches patterns against known fraud typologies (e.g., structuring, card testing).
3.  **Compliance Specialist:** Checks against AML/KYC regulations and sanctions lists.
4.  **Chief Risk Decision Officer:** Synthesizes all findings into a final recommendation (CLEAR, BLOCK, or ESCALATE).

### 2.3 Explainable AI (XAI)
The system uses **SHAP (SHapley Additive exPlanations)** to provide feature attribution for ML decisions. This ensures that every "Black Box" score comes with a human-readable explanation of *why* it was flagged.

---

## 3. Data Flow

1.  **Ingestion:** A transaction is POSTed to `/transactions/ingest`.
2.  **Scoring:** The `HybridScorer` evaluates the transaction in real-time.
3.  **Alerting:** If the score is high, an `Alert` is created and broadcast via **WebSockets** to the dashboard.
4.  **Investigation:** A **Celery** worker triggers the CrewAI investigation asynchronously.
5.  **Reporting:** Agents query the database and RAG knowledge base to produce a structured `InvestigationReport`.
6.  **Resolution:** The final report is saved and pushed to the frontend for analyst review.

---

## 4. Project Structure

### Backend (`txguard-api/`)
- `api/`: FastAPI routes, SQLAlchemy models, and Pydantic schemas.
- `agents/`: CrewAI logic and specialized tools (database, RAG, compliance).
- `ml/`: Scoring engine, feature engineering, and SHAP explainer.
- `workers/`: Celery app for async task management.
- `data/`: Scripts for generating synthetic transaction data.

### Frontend (`txguard-frontend/`)
- `src/app/`: Next.js pages (Dashboard, Alerts, Model Health).
- `src/components/`: Reusable UI components (Risk badges, Score rings, Live pulses).
- `src/hooks/`: Custom hooks for WebSockets and API data fetching.

---

## 5. Setup Requirements

To run TxGuard AI effectively, you need:

1.  **Python 3.13+**: For the backend API and agent layer.
2.  **Node.js**: For the Next.js frontend.
3.  **PostgreSQL**: The primary relational database.
4.  **Redis**: Used as the Celery broker and for velocity counters.
5.  **ChromaDB**: Vector database for RAG-based investigation.
6.  **LLM API Key**: An OpenRouter or OpenAI API key is required for the agents (e.g., GPT-4o or Claude 3.5 Sonnet).

### Configuration
Create a `.env` file in the root and `txguard-api/` with:
- `DATABASE_URL`
- `REDIS_URL`
- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`

---

## 6. Key Value Proposition
TxGuard is designed for **Auditability**. Every decision — from the raw rule trigger to the final agent recommendation — is logged in an immutable `AuditLog`, making it suitable for highly regulated financial environments.
