# =============================================================================
# Ecommerce Customer Service Agent — Single Dockerfile (multi-stage)
# =============================================================================
#
# ONE image, TWO services.
# docker-compose.yml overrides CMD per service:
#
#   agent:     uvicorn app.main:app --host 0.0.0.0 --port 8000
#   mcp-tools: python -m tools_mcp.server
#
# Build strategy:
#   Stage 1 (builder) — compilers + libpq-dev to compile C extensions, builds .venv
#   Stage 2 (runtime) — clean slim image, copies only .venv + source from builder
#
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: builder — fat image with compilers, produces a complete .venv
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# deps layer — cached until uv.lock changes
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# source layer — install project into the same .venv
COPY . .
RUN uv sync --frozen --no-dev

# -----------------------------------------------------------------------------
# Stage 2: runtime — clean slim image, no compilers
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

# curl: healthcheck; libpq5: psycopg runtime (no compile headers needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the fully-built venv and application source from the builder stage
COPY --from=builder /app /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
