# Quick Start Guide

## ✅ Initialization Complete!

Your AutoGen Agent Studio environment is ready to run locally.

## 🎯 What's Ready

- ✅ FastAPI application with async support
- ✅ SQLAlchemy 2.0 database with 6 models
- ✅ Alembic migrations configured
- ✅ RESTful API endpoints for agents, analytics, and chat
- ✅ Pydantic schemas for validation
- ✅ Type checking with pyrefly
- ✅ Testing with pytest (5 tests passing)
- ✅ Code formatting with ruff
- ✅ Comprehensive documentation

## 🚀 Quick Start

### 1. Start the server

```bash
./run.sh
```

The script always applies Alembic migrations before booting Uvicorn, so the
SQLite schema stays in sync automatically. To launch the API manually:

```bash
uv run alembic upgrade head
uv run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Launch the frontend (optional)

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE_URL` in `frontend/.env` if your backend runs on a different
origin (defaults to `http://localhost:8000/api`).

### 3. Access the API

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

### 4. Try it out

Create an agent:
```bash
curl -X POST 'http://localhost:8000/api/agents/' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "My First Agent",
    "type": "assistant",
    "description": "A helpful assistant",
    "initial_config": {"model": "gpt-4"}
  }'
```

List agents:
```bash
curl http://localhost:8000/api/agents/
```

Seed demo analytics data (optional):
```bash
uv run python -m backend.app.scripts.seed_analytics
```
The script creates a "demo" superuser (`analytics@example.com`, password
`AnalyticsDemo!123`) plus representative metrics so dashboards render with
meaningful data. Authentication is currently optional during development: the
API automatically provisions a guest superuser if none exists, so the frontend
works out-of-the-box even without running the seed script.

## 📚 Available Endpoints

### Agents API
- `POST /api/agents/` - Create new agent
- `GET /api/agents/` - List all agents
- `GET /api/agents/{id}` - Get agent details
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent

### Chat API
- `POST /api/chat/sessions/` - Start conversation
- `GET /api/chat/sessions/` - List conversations
- `GET /api/chat/sessions/{id}` - Get conversation
- `POST /api/chat/sessions/{id}/messages/` - Send message
- `GET /api/chat/sessions/{id}/messages/` - Get messages

### Analytics API
- `GET /api/analytics/metrics/summary` - Aggregate metrics (cost, tokens, calls)
- `GET /api/analytics/usage/statistics` - Usage snapshot for the current user
- `GET /api/analytics/performance/statistics` - Latency and reliability per operation
- `GET /api/analytics/costs/breakdown` - Cost breakdown by agent or conversation

### System
- `GET /` - API info
- `GET /api/health` - Health check

## 🧪 Testing

Run backend tests:
```bash
cd backend
uv run pytest
```

Run a specific backend test:
```bash
uv run pytest tests/test_agent_service.py::test_create_agent -v
```

Frontend checks:
```bash
cd frontend
npm run typecheck
npm run test
```

## 🛠️ Development

### Code Formatting
```bash
uv run ruff format .
```

### Linting
```bash
uv run ruff check .
```

### Type Checking
```bash
uv run pyrefly check
```

### Database Migrations

Create a new migration:
```bash
cd backend
uv run alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
uv run alembic upgrade head
```

Rollback migration:
```bash
uv run alembic downgrade -1
```

## 📁 Project Structure

```
agents-builder/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   ├── config.py         # Settings
│   │   ├── database.py       # DB connection
│   │   └── main.py           # FastAPI app
│   ├── alembic/              # Migrations
│   ├── tests/                # Tests
│   └── pytest.ini
├── run.sh                    # Startup script
├── README.md                 # Full documentation
├── USERS_GUIDE.md            # Detailed setup/usage guide
├── TODO.md                   # Project roadmap
└── pyproject.toml            # Dependencies
```

## 🔧 Configuration

Edit `.env` to configure:
- Database URL
- CORS origins
- Debug mode
- API settings

## 📖 Next Steps

1. Review the TODO.md file for the full project roadmap
2. Explore the interactive API docs at `/docs`
3. Start implementing Phase 1 MVP features:
   - [ ] WebSocket support for real-time chat
   - [ ] AutoGen integration layer
   - [ ] Execution logging system
   - [ ] Agent versioning enhancements
   - [ ] MCP server integration

## 💡 Tips

- API docs are interactive - you can test endpoints directly in the browser
- Use the health endpoint to verify the server is running
- Check logs for debugging (server outputs to console)
- Tests run against an in-memory SQLite database
- All code follows the guidelines in CLAUDE.md

The frontend navigation bar lets you switch between the Agent Interaction graph
and the Analytics Dashboard. Provide a bearer token (see `USERS_GUIDE.md`) to
unlock analytics calls.

## 🐛 Troubleshooting

**Port already in use?**
```bash
# Use a different port
uv run uvicorn backend.app.main:app --reload --port 8001
```

**Seeing Pydantic warnings about Python 3.14?**
```bash
# Recreate the environment on Python 3.12
uv sync --python 3.12
```

**Database issues?**
```bash
# Reset database
rm agents_studio.db
cd backend && uv run alembic upgrade head
```

**Import errors?**
```bash
# Ensure you're running from project root
cd /path/to/agents-builder
uv run uvicorn backend.app.main:app --reload
```

---

Happy coding! 🎉
