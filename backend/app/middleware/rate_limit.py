"""Rate limiting middleware using SlowAPI."""

from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.app.config import settings


def get_rate_limiter() -> Limiter:
    """
    Create and configure rate limiter.

    Returns:
        Configured Limiter instance with remote address key function.
    """
    return Limiter(
        key_func=get_remote_address,
        default_limits=[settings.rate_limit_default]
        if settings.rate_limit_enabled
        else [],
        enabled=settings.rate_limit_enabled,
    )


# Global rate limiter instance
limiter = get_rate_limiter()
