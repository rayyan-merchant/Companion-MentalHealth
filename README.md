# Companion

Companion is a non-clinical wellness reflection app for Pakistani university
students. It combines deterministic signal extraction, a versioned YAML rule
catalog, safety interception, explainable evidence, session history, and
optional provider-assisted phrasing.

Companion is not a diagnosis, therapist, emergency service, or substitute for
professional care.

## Architecture

- React, TypeScript, Tailwind CSS, and TanStack Query
- FastAPI with async SQLAlchemy
- PostgreSQL in production and SQLite for local development/tests
- Redis-backed production rate limits and dashboard observation cache
- Opaque hashed session tokens in `HttpOnly`, `Secure`, `SameSite=Lax` cookies
- Double-submit CSRF protection for every state-changing request
- Versioned runtime rules in `reasoning/rules/catalog.v1.yaml`
- OWL, RDF, and SPARQL retained only as research-validation artifacts
- Deterministic responses by default; Groq/Gemini phrasing is opt-in

## Local Development

Requirements: Python 3.11+, Node.js 22+, and optionally Docker Desktop.

```powershell
python -m pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn backend.main:app --reload --port 8000
```

In a second terminal:

```powershell
cd frontend
npm ci
npm run dev
```

The frontend runs at `http://localhost:3000` and proxies `/api` to port 8000.
SQLite and an in-memory rate-limit fallback are used outside production.

## Production-Like Docker

```powershell
docker compose up --build
```

This starts PostgreSQL, Redis, runs Alembic migrations, and serves the same-origin
frontend/API at `http://localhost:10000`.

Production requires explicit `DATABASE_URL`, `REDIS_URL`,
`CORS_ALLOWED_ORIGINS`, and `SUPPORT_EMAIL` settings. PostgreSQL and Redis
readiness are checked by `/api/ready`.

## Render Deployment

The production Render stack is defined in `render.yaml` and includes the Docker
web service, PostgreSQL, Redis-compatible Key Value, migrations, readiness
checks, and daily retention cleanup. See [DEPLOY_RENDER.md](DEPLOY_RENDER.md)
for the safe migration and deployment procedure.

## Legacy Data Import

The importer preserves legacy UUIDs, timestamps, metadata, and soft-deletion
state. It is idempotent and never modifies the source JSON.

```powershell
python -m backend.import_json --data-dir .\data
```

## Account Administration

The beta uses support-assisted recovery rather than a public reset endpoint.

```powershell
python -m backend.admin reset-password --email student@example.com
```

The command prints a one-time temporary password, revokes existing sessions,
requires a password change, and records an audit event.

Retention cleanup can be scheduled daily:

```powershell
python -m backend.maintenance purge
```

Deleted conversations are purged after 30 days by default. Redacted audit and
safety records are retained for 90 days.

## Verification

```powershell
python -m unittest discover -s tests -v
cd frontend
npm test
npm run lint
npm run build
npm audit --audit-level=high
```

Playwright tests target a running app:

```powershell
npm run test:e2e
```

The versioned JSONL evaluation corpus covers extraction, negation, crisis
detection, medical red flags, inference, and false positives. It is a regression
suite, not evidence of clinical accuracy.

## Privacy and Safety

The app includes public Privacy and Safety pages covering stored data, optional
provider processing, retention, deletion, emergency limitations, and
Pakistan-specific resources. Logs contain request metadata and redacted rule
information, not raw mental-health messages or credentials.

Unrestricted public release remains gated on clinician review of the evaluation
corpus, rule thresholds, coping content, and regional crisis resources.

## License

All rights are reserved by the project authors. Permission is required for
reuse, modification, or distribution.
