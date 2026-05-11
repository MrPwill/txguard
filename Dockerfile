# Stage 1: Frontend Build
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY txguard-frontend/package*.json ./
RUN npm ci

COPY txguard-frontend/ ./
# Inject API URLs for production routing via Nginx proxy
ENV NEXT_PUBLIC_API_URL=/api/v1
ENV NEXT_PUBLIC_WS_URL=/alerts/live

RUN npm run build

# Stage 2: Final Image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    ca-certificates \
    nginx \
    supervisor \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install uv for python management
RUN pip install uv

WORKDIR /app

# Setup API
COPY txguard-api/pyproject.toml txguard-api/uv.lock /app/txguard-api/
RUN cd /app/txguard-api && uv sync --frozen

COPY txguard-api/ /app/txguard-api/

# Setup Frontend
COPY --from=frontend-builder /app/frontend/.next/standalone /app/frontend
COPY --from=frontend-builder /app/frontend/.next/static /app/frontend/.next/static
COPY --from=frontend-builder /app/frontend/public /app/frontend/public

# Copy configs
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/supervisord.conf /etc/supervisord.conf
COPY docker/seed.py /app/seed.py

EXPOSE 8080

CMD ["supervisord", "-c", "/etc/supervisord.conf"]
