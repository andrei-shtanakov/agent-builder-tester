# User's Guide – AutoGen Agent Studio

This guide walks you through preparing the environment, running the backend and
frontend, seeding demo analytics data, authenticating, and exploring the product
features.

## 1. Prerequisites

- Python 3.12.x (required)
- [uv](https://github.com/astral-sh/uv) for Python dependency management
- Node.js 20+ and npm for the React frontend
- SQLite (bundled) – no manual setup needed

## 2. Backend Setup

Install dependencies and start the API (from the repository root):

```bash
uv sync
./run.sh
```

The startup script applies Alembic migrations on every run, ensuring the SQLite
schema matches the latest code. To run manually, invoke
`uv run alembic upgrade head` followed by `uv run uvicorn backend.app.main:app`
with your desired host/port.

Available endpoints:
- FastAPI docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/api/health

## 3. Seed Demo Analytics Data (Optional but recommended)

Populate the database with a superuser, agent, conversation, and recent metrics
so the analytics dashboard looks alive:

```bash
uv run python -m backend.app.scripts.seed_analytics
```

The script is idempotent. It creates:
- Superuser: `analytics@example.com`
- Username alias: `analytics-demo`
- Password: `AnalyticsDemo!123`
- Demo agent, conversation, cost/token/API-call metrics, performance metrics, and
  quota data.

> **Note**
> Authentication is currently optional during development. When no accounts are
> present, the backend auto-provisions a "guest" superuser so the UI can make
> protected calls without a token. Run the seed script only if you need the
> richer analytics dataset or want to exercise the login flow.

## 4. Authentication and Tokens

If you choose to authenticate explicitly, request a token using the seeded
credentials:

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=analytics-demo&password=AnalyticsDemo!123"
```

Paste the resulting `access_token` into the login form or use it for API
requests. When you skip this step the frontend operates under the guest
superuser context.

## 5. Frontend Setup & Development Server

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server runs on http://localhost:5173. Configure a custom backend
origin via `frontend/.env`:

```
VITE_API_BASE_URL=http://localhost:8000/api
```

## 6. Exploring the UI

### Navigation
Use the buttons at the top of the interface to switch between:
1. **Chat Sessions** – conversation list, message history, and execution logs.
2. **Agent Interactions** – visualises group chat message flow.
3. **Analytics Dashboard** – usage cards, cost/token trend charts, and
   performance tables.

### Chat Sessions View
- Browse existing conversations, view message history, and stream execution logs.
- Compose new messages or start fresh sessions for any agent.

### Agent Interactions View
- Pick a group chat from the dropdown.
- The graph node size reflects message volume, while edge thickness shows turn
  transitions between participants.

### Analytics Dashboard View
- Adjust the date range, target operation (`agent.run` by default), and cost
  entity filters.
- Metric cards summarise cost, tokens, API calls, and error rate.
- Trend charts plot daily cost and token usage over the selected period.
- Tables provide details for usage statistics, operation performance, and cost
  breakdowns.
- Use **Refresh** to re-query data without reloading the page.

## 7. Testing & Quality Checks

Backend:
```bash
uv run ruff check .          # lint
uv run pyrefly check         # static types
uv run pytest                # backend tests
```

Frontend:
```bash
cd frontend
npm run typecheck
npm run test
```

Vitest runs in watch mode; press `q` to exit.

## 8. Maintenance Tips

- **Re-seed demo data** anytime with `uv run python -m backend.app.scripts.seed_analytics`.
- **Reset SQLite database** by deleting `agents_studio.db` and running
  migrations again.
- **Update dependencies** via `uv add` / `npm update` following repository
  guidelines.

## 9. Project Roadmap

A comprehensive backlog lives in `TODO.md`. Many frontend items (chat UI, log
panel, MCP tooling) are still unchecked and make excellent next steps once the
analytics foundation is validated.

## 10. Support

If the API rejects requests with `401 Unauthorized`, verify that the bearer
token is saved in the frontend and has not expired (generate a fresh token using
section 4). For rate-limit errors, slow down or raise limits during development.
