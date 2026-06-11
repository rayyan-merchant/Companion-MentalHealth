# ==========================================
# Stage 1: Build Frontend
# ==========================================
FROM node:22-alpine as frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ .
RUN npm run build

# ==========================================
# Stage 2: Setup Backend & Runtime
# ==========================================
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (build-essential might be needed for some python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && \
    pip install --default-timeout=1000 --no-cache-dir -r requirements.txt


# Copy backend code
COPY backend/ ./backend/
COPY agents/ ./agents/
COPY alembic/ ./alembic/
COPY alembic.ini ./alembic.ini

# Copy knowledge base directories (required by symbolic reasoner)
COPY ontology/ ./ontology/
COPY reasoning/ ./reasoning/
COPY nlp/ ./nlp/
COPY graph/ ./graph/

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Run as a non-root user.
RUN useradd --create-home --uid 10001 appuser && \
    chown -R appuser:appuser /app

# Set Environment Variables
ENV PYTHONPATH=/app
ENV PORT=10000
ENV APP_ENV=production

# Expose port
EXPOSE 10000

USER appuser

# Database migrations run as Render's pre-deploy command in production.
CMD ["sh", "-c", "exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
