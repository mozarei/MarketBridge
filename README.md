# MarketBridge (Crosslist App)

Monorepo for a cross-listing system with:

- `backend`: FastAPI + SQLAlchemy + Postgres + Redis + Celery
- `web`: Next.js admin dashboard (App Router)
- `mobile`: Flutter app scaffold
- `infra`: Docker Compose for local development

## Repo Layout

```text
crosslist-app/
  backend/
    app/
      api/
      core/
      db/
      models/
      schemas/
      tasks/
    alembic/
    alembic.ini
    Dockerfile
    requirements.txt
  web/
    src/app/
    src/lib/
  mobile/
  infra/
    docker-compose.yml
```

## Architecture

Core principle: clients never call marketplaces directly.

- Flutter + Web call FastAPI only.
- FastAPI stores source-of-truth data in Postgres.
- FastAPI enqueues background jobs to Celery.
- Celery uses Redis as broker/backend and updates Postgres state.
- `sync_events` stores operational logs and outcomes.

## Implemented Backend Features

- Auth:
  - `POST /auth/register`
  - `POST /auth/login`
  - `GET /auth/me`
- Items:
  - `POST /items`
  - `GET /items`
  - `GET /items/{item_id}`
  - `PATCH /items/{item_id}`
  - `DELETE /items/{item_id}`
  - `POST /items/{item_id}/publish` (enqueues Celery job)
- Jobs:
  - `GET /jobs/{job_id}`
- Orders:
  - `GET /orders`
- Events:
  - `GET /events?limit=100`
- Health:
  - `GET /health`

### Current Auth Model (Local Dev)

Protected routes use header:

- `X-User-Id: <user_id>`

This is a temporary local-dev approach before JWT/session auth.

## Data Model (MVP)

- `users`
- `connections`
- `items`
- `channel_listings`
- `orders`
- `sync_events`

Migrations are managed with Alembic.

## Celery Tasks (Stubbed)

- `jobs.publish_item`
- `jobs.sync_orders`
- `jobs.auto_delist`

Each task logs started/succeeded/failed events into `sync_events`.

## Web Dashboard

- Home: `/`
- Events page: `/events`
  - Reads from backend `GET /events`
  - Displays event status, type, job id, and message

Environment variables used in web:

- `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`)
- `NEXT_PUBLIC_DEV_USER_ID` (default `1`)

## Local Run

From repo root:

```bash
docker compose -f infra/docker-compose.yml up -d db redis
docker compose -f infra/docker-compose.yml run --rm api alembic upgrade head
docker compose -f infra/docker-compose.yml up -d --build api worker
```

Check backend:

```bash
curl http://localhost:8000/health
```

Run web (new terminal):

```bash
cd web
npm install
npm run dev
```

Open:

- `http://localhost:3000`
- `http://localhost:3000/events`

## End Of Work (Stop/Cleanup)

When you are done working, stop background services:

```bash
docker compose -f infra/docker-compose.yml down
```

Optional: also remove Postgres data volume (this resets local DB data):

```bash
docker compose -f infra/docker-compose.yml down -v
```

Optional: remove app images to free disk (they rebuild on next run):

```bash
docker rmi infra-api:latest infra-worker:latest
```

Optional: broader Docker cleanup (removes unused images/containers/networks across your machine):

```bash
docker system prune -a
```

To start again later:

```bash
docker compose -f infra/docker-compose.yml up -d db redis
docker compose -f infra/docker-compose.yml run --rm api alembic upgrade head
docker compose -f infra/docker-compose.yml up -d --build api worker
```

## Smoke Test (API)

```bash
REGISTER=$(curl -s -X POST http://localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"moe@example.com","password":"password123"}')

echo "$REGISTER"

USER_ID=$(echo "$REGISTER" | sed -n 's/.*"user_id_header_value":\([0-9]*\).*/\1/p')

ITEM=$(curl -s -X POST http://localhost:8000/items \
  -H 'Content-Type: application/json' \
  -H "X-User-Id: $USER_ID" \
  -d '{"title":"Test Jacket","description":"Black denim","price_cents":4500,"currency":"USD","quantity":1}')

echo "$ITEM"

ITEM_ID=$(echo "$ITEM" | sed -n 's/.*"id":\([0-9]*\).*/\1/p')

PUBLISH=$(curl -s -X POST "http://localhost:8000/items/$ITEM_ID/publish" \
  -H 'Content-Type: application/json' \
  -H "X-User-Id: $USER_ID" \
  -d '{"channel":"ebay"}')

echo "$PUBLISH"

JOB_ID=$(echo "$PUBLISH" | sed -n 's/.*"job_id":"\([^"]*\)".*/\1/p')

curl -s "http://localhost:8000/jobs/$JOB_ID"; echo
curl -s -H "X-User-Id: $USER_ID" http://localhost:8000/events; echo
```

## Next Recommended Work

1. Replace `X-User-Id` with JWT auth.
2. Add web pages for items and orders.
3. Integrate real marketplace adapters in Celery tasks.
4. Add retry/backoff policy and dead-letter handling.
