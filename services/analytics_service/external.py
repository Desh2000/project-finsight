# FinVest | Analytics Service | external.py
# Member 4: Savings Goal & Portfolio Analytics — Frankfurter API integration (USD → LKR)

import requests
import time
from datetime import datetime, timezone

# ── In-memory exchange rate cache with 5-minute TTL ──
_rate_cache: dict = {}  # { "rate": float, "timestamp": float, "fallback": bool }
CACHE_TTL_SECONDS = 300  # 5 minutes
FALLBACK_RATE = 320.0  # Hardcoded fallback USD→LKR rate


def get_usd_to_lkr() -> tuple[float, bool, str]:
    """
    Fetch the live USD→LKR exchange rate from Frankfurter API.
    Returns: (rate, is_fallback, timestamp_iso)
    Uses a 5-minute cache. Falls back to 320.0 LKR/USD if API is unavailable.
    """
    now = time.time()

    # Check cache
    if _rate_cache and (now - _rate_cache["timestamp"]) < CACHE_TTL_SECONDS:
        return (
            _rate_cache["rate"],
            _rate_cache["fallback"],
            datetime.fromtimestamp(_rate_cache["timestamp"], tz=timezone.utc).isoformat(),
        )

    # Fetch from Frankfurter API
    try:
        resp = requests.get(
            "https://api.frankfurter.app/latest",
            params={"from": "USD", "to": "LKR"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        rate = data.get("rates", {}).get("LKR")

        if rate is not None:
            _rate_cache["rate"] = rate
            _rate_cache["timestamp"] = now
            _rate_cache["fallback"] = False
            return rate, False, datetime.fromtimestamp(now, tz=timezone.utc).isoformat()
    except Exception:
        pass

    # Fallback: use hardcoded rate
    _rate_cache["rate"] = FALLBACK_RATE
    _rate_cache["timestamp"] = now
    _rate_cache["fallback"] = True
    return FALLBACK_RATE, True, datetime.fromtimestamp(now, tz=timezone.utc).isoformat()
