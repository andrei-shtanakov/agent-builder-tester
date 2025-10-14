# TODO.md - AutoGen Agent Studio

## Snapshot
This roadmap captures planned capabilities. Completed items are checked, in-progress or
upcoming items remain unchecked. Frontend work now includes a functional analytics
dashboard; core chat, configuration, and logging modules are still pending.

---

## Tech Stack

### Frontend
- [x] React 18 with hooks
- [x] TypeScript
- [x] Zustand state management
- [x] React Query for API interactions
- [ ] WebSocket client for real-time logs
- [ ] React Router-based navigation (current navigation is manual)
- [ ] Monaco Editor integration (planned)

### Backend
- [x] Python 3.12 / FastAPI
- [x] SQLAlchemy 2.0 with Alembic migrations
- [x] SQLite (development), PostgreSQL-ready
- [x] Pydantic models & schemas
- [x] Analytics, agents, auth, group chat services
- [ ] AutoGen orchestration layer (stubbed)
- [ ] WebSocket endpoints for live chat/log updates

### Infrastructure
- [ ] Docker & Docker Compose environment
- [ ] Nginx reverse proxy configuration
- [ ] Redis integration for queues/caching

---

## Feature Modules

### 1. Chat Interface
- [ ] Real-time conversation UI & streaming
- [ ] Multi-turn dialog support in frontend
- [ ] Message history pagination in UI
- [ ] Agent picker & status indicators
- [ ] Markdown rendering for responses
- [ ] Message composer with auto-resize & reset

### 2. Logs & Execution Panel
- [ ] Live log feed (WebSocket)
- [ ] Execution details (parameters, outputs)
- [ ] Metrics overlay (latency, tokens) per execution
- [ ] Log filtering/search, export, auto-scroll controls
- [x] Agent interaction graph (backend + frontend graph view)

### 3. Agent Configuration Studio
- [ ] CRUD UI for agents and versions
- [ ] Prompt editor & parameter controls
- [ ] Tool/MCP configuration workflows
- [x] Group chat settings API + basic UI integration
- [ ] Configuration validation & preview/test harness

### 4. Analytics & Metrics
- [x] Metric & performance models + services
- [x] API endpoints (`/metrics`, `/usage`, `/performance`, `/costs`)
- [x] Frontend dashboard cards & tables
- [x] Trend charts (cost & tokens)
- [ ] Comparative metrics (multi-series charts, per-agent summaries)
- [ ] Export/reporting options

### 5. Authentication & Users
- [x] Registration/login/token issuance
- [x] Seed script for demo superuser + analytics data
- [ ] Frontend login flow (UI form, token storage without manual paste)
- [ ] Role-based UI access (hide analytics for non-auth users)

---

## Testing & Quality
- [x] Backend pytest suite (agents, analytics, auth, group chat, logs, rate limits)
- [x] Ruff lint + Pyrefly type checking
- [x] Frontend typecheck (tsc) & Vitest coverage for analytics widgets
- [ ] End-to-end tests (Playwright/Cypress) covering login + dashboards
- [ ] Load testing for analytics endpoints

---

## Documentation
- [x] README overview and setup instructions
- [x] QUICKSTART for quick setup
- [x] USERS_GUIDE with detailed workflow
- [ ] API reference (OpenAPI docs refinement)
- [ ] Developer guide for contribution workflow & coding standards

---

## Near-Term Focus (suggested backlog)
1. Reinstate secure authentication (remove guest fallback, wire login UI end-to-end).
2. Implement WebSocket-based log streaming and surface live events in the chat view.
3. Expand chat interface with pagination, markdown rendering, and agent status.
4. Containerise application with Docker Compose for reproducible dev environments.

---

## Notes
- Demo analytics data is generated via `uv run python -m backend.app.scripts.seed_analytics`.
- Current navigation is tab-based; React Router remains an optional enhancement.
- Backend now provisions a guest superuser automatically; remove this fallback
  once the secure auth flow is restored.
- Many legacy sections from earlier plans were trimmed to reflect today’s status;
  reintroduce as tasks become active.
