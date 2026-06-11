# Deploying Companion on Render

Companion remains deployable on Render, but the production architecture now
requires three persistent resources:

- A Docker web service
- Render Postgres
- Render Key Value (Redis-compatible)

The included `render.yaml` also creates a daily cron job for retention cleanup.

## Recommended Cutover

Keep the old service live while creating the new production stack. This avoids
turning a persistence migration into an in-place outage.

1. Push the current branch to the Git provider connected to Render.
2. In Render, choose **New > Blueprint** and select this repository.
3. Render will detect `render.yaml`. Review and create the resources.
4. When prompted, set:
   - `SUPPORT_EMAIL` to the monitored recovery address.
   - `CORS_ALLOWED_ORIGINS` to the new web service's exact HTTPS origin.
5. Leave `COOKIE_DOMAIN` unset. Host-only cookies are the safer default.
6. Wait for the Postgres and Key Value resources to become available.
7. Confirm the pre-deploy migration succeeds and `/api/ready` returns HTTP 200.
8. Test signup, login, logout, chat, sessions, dashboard, privacy, and safety.
9. Move the custom domain to the new service, or use the new Render URL.
10. Only retire the old service after the production checks pass.

The Blueprint creates resources in Singapore, Render's nearest available region
for the Pakistan beta. All resources must remain in the same Render region.

## Existing Render Service

An existing service can be reused only if its Render runtime is already
**Docker**. Render does not allow changing a service runtime after creation.
For a native Python or Node service, create the Blueprint stack as a new service
and cut traffic over after verification.

To reuse an existing Docker service manually:

1. Create Postgres and Key Value in the same region as the web service.
2. Set the environment variables listed below.
3. Set the pre-deploy command to `python -m alembic upgrade head`.
4. Set the health check path to `/api/ready`.
5. Deploy the latest commit.

## Required Environment

```text
APP_ENV=production
DATABASE_URL=<Render Postgres internal connection string>
REDIS_URL=<Render Key Value internal connection string>
SUPPORT_EMAIL=<monitored support address>
CORS_ALLOWED_ORIGINS=https://<exact-public-host>
ENABLE_LLM=false
ENABLE_EMBEDDINGS=false
ENABLE_VECTOR_MEMORY=false
PREWARM_CONCEPT_EMBEDDINGS=false
```

Use internal connection strings, not public database credentials. Do not set
`COOKIE_DOMAIN` unless cookies deliberately need to span custom subdomains.

External phrasing is optional. Enable it only after updating the public privacy
notice and adding the relevant provider key in Render:

```text
ENABLE_LLM=true
GROQ_API_KEY=<secret>
```

The deterministic response path remains active if the provider is disabled,
fails, or exceeds its time budget.

## Legacy JSON Data

The Docker image intentionally excludes legacy JSON containing user and
conversation data. Do not commit or bake this sensitive data into the image.

If the old deployment contains data that must be retained, export it before
redeploying the old service. Transfer it through an approved private channel,
then run this once against the new Postgres database:

```text
python -m backend.import_json --data-dir /path/to/data
```

The importer is idempotent and preserves UUIDs, timestamps, metadata, and
soft-deletion state. Users will still be logged out at cutover because the new
authentication system uses server-side cookie sessions.

If the existing Render service stored JSON only on its local filesystem, treat
the export as urgent: Render service filesystems are ephemeral.

## Post-Deploy Operations

Readiness:

```text
GET https://<host>/api/ready
```

Administrator-assisted account recovery:

```text
python -m backend.admin reset-password --email student@example.com
```

Manual retention cleanup:

```text
python -m backend.maintenance purge
```

Do not use free Postgres for a public beta. Render's free Postgres expires after
30 days and has no backups. Free Key Value can lose all rate-limit and cache
state on restart. The Blueprint therefore selects paid starter/basic resources.
