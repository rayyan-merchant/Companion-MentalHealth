# ==========================================
# Stage 1: Build Frontend
# ==========================================
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

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
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY agents/ ./agents/
COPY data/ ./data/

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Set permissions for data directory (Important for SQLite/JSON persistence in Docker)
RUN chmod -R 777 ./data

# Set Environment Variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose port
EXPOSE 8000

# Run Application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
