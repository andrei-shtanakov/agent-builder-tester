#!/bin/bash

# AutoGen Agent Studio - Development Server Startup Script

set -e

# Change to script directory
cd "$(dirname "$0")"

echo "🚀 Starting AutoGen Agent Studio..."

echo "📦 Applying database migrations..."
cd backend
uv run alembic upgrade head
cd ..
echo "✓ Database ready"

# Start the server
echo "🌐 Starting server on http://localhost:8000"
echo "📚 API docs available at http://localhost:8000/docs"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

uv run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
