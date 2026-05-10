FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    ca-certificates \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY txguard-api/pyproject.toml txguard-api/uv.lock /app/txguard-api/
RUN cd /app/txguard-api && uv sync --frozen

COPY txguard-api/ /app/txguard-api/

COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/supervisord.conf /etc/supervisord.conf

RUN mkdir -p /var/log /app/dist

COPY docker/seed.py /app/seed.py

EXPOSE 8080

CMD ["supervisord", "-c", "/etc/supervisord.conf"]