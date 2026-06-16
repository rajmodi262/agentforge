"""AgentForge AI — Shared Rate Limiter

Single limiter instance shared across all API modules.
Avoids circular imports between main.py and auth.py.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
