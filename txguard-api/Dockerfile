FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY txguard-api/pyproject.toml /app/txguard-api/
RUN pip install uv && uv sync --frozen

WORKDIR /app/txguard-api

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]