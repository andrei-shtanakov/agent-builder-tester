# AutoGen Agent Studio

Web platform for creating, configuring, testing, and managing AI agents based on
Microsoft AutoGen with an interactive user interface.

## Features

- **Agent Management**: Create, update, and manage AI agents with versioning
- **Chat Interface**: Real-time communication with AI agents
- **Agent Configuration**: Flexible configuration with system prompts and model
  settings
- **Database**: SQLAlchemy 2.0 with Alembic migrations
- **Analytics Insights**: Usage, cost, and performance dashboards for agents
  including time-series visualisations
- **Type Safety**: Full type checking with pyrefly
- **Testing**: Comprehensive pytest suite

## Tech Stack

### Backend
- Python 3.12.x
- FastAPI (async REST API)
- SQLAlchemy 2.0 (ORM)
- Alembic (database migrations)
- Pydantic (data validation)
- AutoGen (pyautogen)
- SQLite (PostgreSQL for production)

### Frontend
- React 18 with TypeScript
- Vite dev server and build pipeline
- TanStack Query for data fetching
- Zustand for lightweight state management

## Getting Started

### Prerequisites

- Python 3.12.x (see guidance below)
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd agents-builder
   ```
2. Install dependencies:
   ```bash
   uv sync
   ```
   If you created an environment on a different interpreter, recreate it with:
   ```bash
   uv sync --python 3.12
   ```
3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
4. Run database migrations:
   ```bash
   cd backend
   uv run alembic upgrade head
   ```

### Python Version Guidance

AutoGen Agent Studio targets Python 3.12.x. Newer interpreters such as Python
3.14 trigger warnings in transitive dependencies (notably Pydantic). Stay on
Python 3.12 to avoid those issues. The repository ships with a `.python-version`
file to help your tooling pick the correct interpreter. If you need to switch,
reinstall the virtual environment using `uv sync --python 3.12`.

### Running the Application

**Quick start:**
```bash
./run.sh
```

Or manually start the development server from the project root:
```bash
uv run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Frontend Development

```bash
cd frontend
npm install  # install Node dependencies (requires Node 20+)
npm run dev  # launches Vite dev server on http://localhost:5173
```

Set the backend origin with `VITE_API_BASE_URL` in a `.env` file inside the
`frontend/` directory (defaults to `http://localhost:8000/api`). The UI expects a
bearer token to access authenticated analytics endpoints—paste it into the token
field on the agent interactions or analytics dashboard pages. Use the navigation
bar to toggle between the interaction graph and the analytics dashboard.

See `USERS_GUIDE.md` for a detailed walkthrough covering authentication,
seeding demo analytics data, and UI usage tips.

### Running Tests

```bash
cd backend
uv run pytest
```

### Seed Demo Analytics Data

Populate the local database with a demo user, agent, and recent analytics
activity:

```bash
uv run python -m backend.app.scripts.seed_analytics
```

This creates a superuser (`analytics@example.com`) with demo metrics that power
the analytics dashboard.

### Code Quality

Format code:
```bash
uv run ruff format .
```

Check code:
```bash
uv run ruff check .
```

Fix linting issues:
```bash
uv run ruff check . --fix
```

Type checking:
```bash
uv run pyrefly check
```

## Project Structure

```
agents-builder/
├── backend/
│   ├── app/
│   │   ├── api/                 # API routes
│   │   ├── models/              # Database models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   ├── config.py            # Settings management
│   │   ├── database.py          # Database connection
│   │   └── main.py              # FastAPI application entrypoint
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Test suite
│   └── pytest.ini
├── run.sh                       # Startup helper script
├── README.md                    # Primary documentation
├── TODO.md                      # Roadmap and features backlog
├── pyproject.toml               # Python project metadata
├── pyrefly.toml                 # Type checker configuration
└── uv.lock                      # Locked dependency versions
```

## API Endpoints

### Agents
- `POST /api/agents` - Create agent
- `GET /api/agents` - List agents
- `GET /api/agents/{id}` - Get agent details
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent

### Chat
- `POST /api/chat/sessions` - Start chat session
- `GET /api/chat/sessions` - List sessions
- `GET /api/chat/sessions/{id}` - Get session details
- `POST /api/chat/sessions/{id}/messages` - Send message
- `GET /api/chat/sessions/{id}/messages` - Get message history

### System
- `GET /` - Root endpoint
- `GET /api/health` - Health check

### Group Chat
- `POST /api/group-chats` - Create group chat
- `GET /api/group-chats` - List group chats
- `GET /api/group-chats/{id}` - Get group chat details
- `PUT /api/group-chats/{id}` - Update group chat
- `DELETE /api/group-chats/{id}` - Delete group chat
- `GET /api/group-chats/{id}/participants` - List group chat participants
- `GET /api/group-chats/{id}/messages` - List messages across group chat conversations

## Development

### Adding a New Model

1. Create model in `backend/app/models/`
2. Create schema in `backend/app/schemas/`
3. Create service in `backend/app/services/`
4. Create API routes in `backend/app/api/`
5. Generate migration: `uv run alembic revision --autogenerate -m "description"`
6. Apply migration: `uv run alembic upgrade head`

### Code Guidelines

- Use `uv` for package management (never `pip`)
- Add type hints to all functions
- Follow PEP 8 naming conventions
- Write docstrings for public APIs
- Keep functions small and focused
- Line length: 88 characters maximum
- Test your changes with pytest

## Troubleshooting

- **Pydantic warnings on Python 3.14**: Recreate your environment with Python
  3.12 using `uv sync --python 3.12`.
- **Database mismatch**: Delete `agents_studio.db` and run `uv run alembic
  upgrade head` from the `backend/` directory.

## License

[Add your license here]
