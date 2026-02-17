from typing import Optional
import os
import logging
import secrets
from datetime import timedelta
from backend.redis_client import get_redis

logger = logging.getLogger("clientflow.sessions")

# Session TTL in seconds (default 7 days)
SESSION_TTL = int(os.getenv("SESSION_TTL_SECONDS", str(7 * 24 * 3600)))


def create_session(empresa_id: int) -> str:
    """Create a session token stored in Redis pointing to `empresa_id`.

    Returns the generated token.
    """
    r = get_redis()
    token = secrets.token_urlsafe(32)
    key = f"session:{token}"
    try:
        r.set(key, str(empresa_id), ex=SESSION_TTL)
    except Exception as e:
        logger.exception("Failed to create session in Redis: %s", e)
        raise
    return token


def get_session_empresa(token: str) -> Optional[int]:
    """Return empresa_id associated with `token`, or None if not found/invalid.

    Access refreshes the TTL for the session.
    """
    r = get_redis()
    key = f"session:{token}"
    try:
        val = r.get(key)
    except Exception as e:
        logger.exception("Redis error on get_session_empresa: %s", e)
        return None
    if val is None:
        return None
    # refresh TTL on access
    try:
        r.expire(key, SESSION_TTL)
    except Exception:
        logger.debug("Could not refresh session TTL for key %s", key)
    try:
        return int(val)
    except Exception:
        logger.debug("Invalid session value for key %s: %r", key, val)
        return None


def revoke_session(token: str) -> None:
    """Remove a single session token."""
    r = get_redis()
    key = f"session:{token}"
    try:
        r.delete(key)
    except Exception as e:
        logger.exception("Failed to delete session %s: %s", key, e)


def revoke_all_sessions_for_empresa(empresa_id: int) -> int:
    """Revoke all sessions for a given `empresa_id`.

    Returns the number of revoked sessions.
    Note: uses `SCAN` which is safe for production; avoid `KEYS`.
    """
    r = get_redis()
    pattern = "session:*"
    revoked = 0
    try:
        for k in r.scan_iter(match=pattern):
            try:
                val = r.get(k)
                if val and int(val) == empresa_id:
                    r.delete(k)
                    revoked += 1
            except Exception:
                # skip malformed values
                continue
    except Exception as e:
        logger.exception("Error while revoking sessions for empresa %s: %s", empresa_id, e)
    return revoked
