# FinVest | Asset Service | external.py
# Member 2: Platform Asset & Market Data — CoinGecko API integration

import requests
import time
from typing import Optional

# ── In-memory price cache with 60-second TTL ──
_price_cache: dict = {}  # { coingecko_id: { "price_usd": float, "timestamp": float } }
CACHE_TTL_SECONDS = 60


def fetch_live_prices(coingecko_ids: list[str]) -> dict[str, Optional[float]]:
    """
    Fetch live USD prices from CoinGecko for the given list of coin IDs.
    Returns a dict mapping coingecko_id → price_usd (or None if unavailable).
    Caches results for 60 seconds to avoid rate limiting.
    """
    now = time.time()
    result: dict[str, Optional[float]] = {}
    ids_to_fetch: list[str] = []

    # Check cache first
    for cg_id in coingecko_ids:
        if cg_id and cg_id in _price_cache:
            cached = _price_cache[cg_id]
            if now - cached["timestamp"] < CACHE_TTL_SECONDS:
                result[cg_id] = cached["price_usd"]
            else:
                ids_to_fetch.append(cg_id)
        elif cg_id:
            ids_to_fetch.append(cg_id)

    # Fetch any non-cached prices from CoinGecko
    if ids_to_fetch:
        try:
            ids_str = ",".join(ids_to_fetch)
            resp = requests.get(
                f"https://api.coingecko.com/api/v3/simple/price",
                params={"ids": ids_str, "vs_currencies": "usd"},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

            for cg_id in ids_to_fetch:
                price = data.get(cg_id, {}).get("usd")
                if price is not None:
                    _price_cache[cg_id] = {"price_usd": price, "timestamp": now}
                    result[cg_id] = price
                else:
                    # Try to use stale cache as fallback
                    if cg_id in _price_cache:
                        result[cg_id] = _price_cache[cg_id]["price_usd"]
                    else:
                        result[cg_id] = None
        except Exception:
            # On failure, use whatever is in the cache (stale data)
            for cg_id in ids_to_fetch:
                if cg_id in _price_cache:
                    result[cg_id] = _price_cache[cg_id]["price_usd"]
                else:
                    result[cg_id] = None

    return result


def is_data_stale(coingecko_id: str) -> bool:
    """Check whether the cached data for a given ID is stale (older than TTL)."""
    if coingecko_id not in _price_cache:
        return True
    return (time.time() - _price_cache[coingecko_id]["timestamp"]) >= CACHE_TTL_SECONDS
