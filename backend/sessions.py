from typing import Optional
import secrets
from datetime import timedelta
from backend.redis_client import get_redis

# Session TTL in seconds (default 7 days)
SESSION_TTL = int(__import__('os').getenv('SESSION_TTL_SECONDS', str(7 * 24 * 3600)))


def create_session(empresa_id: int) -> str:
    """Create a session token stored in Redis pointing to empresa_id."""
    r = get_redis()
    token = secrets.token_urlsafe(32)
    key = f"session:{token}"
    r.set(key, str(empresa_id), ex=SESSION_TTL)
    return token


def get_session_empresa(token: str) -> Optional[int]:
    r = get_redis()
    key = f"session:{token}"
    val = r.get(key)
    if val is None:
        return None
    # refresh TTL on access
    r.expire(key, SESSION_TTL)
    try:
        return int(val)
    except Exception:
        return None


def revoke_session(token: str) -> None:
    r = get_redis()
    key = f"session:{token}"
    r.delete(key)


def revoke_all_sessions_for_empresa(empresa_id: int):
    r = get_redis()
    # WARNING: this uses KEYS which is acceptable for small dev environments but not for production.
    pattern = "session:*"
    for k in r.scan_iter(match=pattern):
        try:
            val = r.get(k)
            if val and int(val) == empresa_id:
                r.delete(k)
        except Exception:
            continue
