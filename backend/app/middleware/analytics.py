"""Middleware for automatic analytics tracking."""

import time
from datetime import datetime, timezone

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from backend.app.database import SessionLocal
from backend.app.models.analytics import PerformanceMetric


class AnalyticsMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically track request performance metrics."""

    async def dispatch(self, request: Request, call_next):
        """Track request timing and status."""
        # Skip tracking for health check and static files
        if request.url.path in ["/health", "/", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        # Record start time
        start_time = time.time()

        # Process the request
        try:
            response: Response = await call_next(request)
            status = "success" if response.status_code < 400 else "error"
            error_message = None
        except Exception as e:
            status = "error"
            error_message = str(e)
            raise
        finally:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Save performance metric asynchronously
            try:
                db = SessionLocal()
                try:
                    metric = PerformanceMetric(
                        operation=f"{request.method} {request.url.path}",
                        duration_ms=duration_ms,
                        status=status,
                        error_message=error_message,
                        extra_metadata={
                            "method": request.method,
                            "path": request.url.path,
                            "status_code": (
                                response.status_code if status == "success" else 500
                            ),
                            "user_agent": request.headers.get("user-agent"),
                        },
                        timestamp=datetime.now(timezone.utc),
                    )
                    db.add(metric)
                    db.commit()
                finally:
                    db.close()
            except Exception:
                # Silently fail - don't let analytics break the app
                pass

        return response
