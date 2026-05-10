# TxGuard AI — Deployment Architecture (Single Container)

## Deployment Goal

Deploy **both frontend + backend in a single Docker container** to either:

- Google Cloud Run
- Azure Container Apps

Infrastructure provisioning will be handled via **Terraform**.

This architecture prioritizes:

- simpler deployments
- easier recruiter demos
- lower operational overhead
- infrastructure-as-code maturity

---

# Updated Deployment Architecture

```text
Single Container
├── Nginx (reverse proxy)
├── Next.js frontend
├── FastAPI backend
├── Celery worker
├── ML models
├── CrewAI agents
├── ChromaDB local vector store
└── Supervisord process manager

Managed Cloud Services
├── PostgreSQL (Cloud SQL / Azure PostgreSQL)
└── Redis (Memorystore / Azure Cache for Redis)
```

---

# Why this architecture?

Previously:

- frontend on Vercel
- backend on Railway
- separate Celery workers
- multiple deployment targets

That creates unnecessary complexity for a portfolio project.

New architecture gives you:

- one deployment artifact
- one CI/CD pipeline
- one Terraform deployment workflow
- easier debugging
- cleaner demo story in interviews

---

# Container Runtime Design

## Nginx

Responsibilities:

- serve Next.js static assets
- reverse proxy frontend requests
- route API calls to FastAPI
- handle websocket upgrades

Example routing:

```text
/ → Next.js frontend
/api/* → FastAPI
/ws/* → FastAPI websocket endpoints
```

---

## Next.js

Frontend will be built using:

```bash
npm run build
npm run export
```

Static output served via nginx.

---

## FastAPI

Handles:

- transaction ingestion
- scoring
- explainability endpoints
- alerts API
- reports API
- websocket connections

Runs via:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Celery Worker

Still retained because investigations may take up to 120 seconds.

Handles:

- async fraud investigations
- CrewAI orchestration
- long-running report generation

Runs via:

```bash
celery -A workers.celery_app worker --loglevel=info
```

---

## Supervisord

Manages all container processes.

```text
supervisord
├── nginx
├── fastapi
└── celery worker
```

---

# Docker Structure

```text
txguard/
├── txguard-api/
├── txguard-frontend/
├── infra/
│   └── terraform/
├── docker/
│   ├── nginx.conf
│   └── supervisord.conf
├── Dockerfile
└── docker-compose.yml
```

---

# Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    curl \
    nodejs \
    npm

COPY txguard-api/ ./txguard-api/
COPY txguard-frontend/ ./txguard-frontend/

RUN pip install -r txguard-api/requirements.txt

WORKDIR /app/txguard-frontend
RUN npm install
RUN npm run build
RUN npm run export

WORKDIR /app

COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8080

CMD ["/usr/bin/supervisord"]
```

---

# Terraform Infrastructure

## GCP

Terraform provisions:

- Cloud Run
- Artifact Registry
- Cloud SQL PostgreSQL
- Memorystore Redis
- service accounts
- IAM roles
- secrets

```text
terraform/gcp/
├── main.tf
├── variables.tf
├── outputs.tf
```

---

## Azure

Terraform provisions:

- Azure Container Apps
- Azure Container Registry
- Azure PostgreSQL
- Azure Cache for Redis
- Key Vault

```text
terraform/azure/
├── main.tf
├── variables.tf
├── outputs.tf
```

---

# CI/CD Flow

```text
GitHub Actions
→ Build Docker image
→ Push image
→ Terraform apply
→ Deploy infrastructure
→ Deploy application
```

---

# Environment Variables

```bash
DATABASE_URL=
REDIS_URL=
OPENAI_API_KEY=
OPENROUTER_API_KEY=
SECRET_KEY=
CHROMA_PATH=
```

---

# Plan.md Changes

Update Phase 6 from:

> Deploy backend on Railway
> Deploy frontend on Vercel

To:

> Build unified Docker container
> Deploy container via Terraform to Cloud Run or Azure Container Apps

Replace current architecture references with:

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
```

---

# Interview Positioning

This architecture tells recruiters:

- you understand full-stack deployment
- you can simplify distributed systems when needed
- you know Terraform
- you understand container orchestration
- you can deploy AI systems in cloud-native environments

That’s significantly stronger than saying:

> “Frontend is here, backend is there, worker is somewhere else.”

