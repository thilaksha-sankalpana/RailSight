"""
TCDAFS - Caching Utilities
Simple in-memory cache to avoid repeated API calls
"""
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Global cache storage
_cache = {}


def get_cached(key, fetch_function, ttl_minutes=5):
    """
    Get data from cache or fetch if expired

    Args:
        key: Cache key (e.g., "stations")
        fetch_function: Function to call if cache miss
        ttl_minutes: Time to live in minutes

    Returns:
        Cached data or fresh data from fetch_function
    """
    global _cache

    # Check if cached and not expired
    if key in _cache:
        data, timestamp = _cache[key]
        if datetime.now() - timestamp < timedelta(minutes=ttl_minutes):
            logger.info(f"Cache HIT for '{key}' (age: {(datetime.now() - timestamp).seconds}s)")
            return data

    # Cache miss or expired - fetch fresh data
    logger.info(f"Cache MISS for '{key}' - fetching fresh data")
    data = fetch_function()

    # Only cache if we got valid data (not None and not empty list)
    if data is not None and data != []:
        _cache[key] = (data, datetime.now())
        logger.info(f"Cached '{key}' with {len(data) if isinstance(data, list) else 'non-list'} items")
    else:
        logger.warning(f"Not caching empty/null result for '{key}'")

    return data


def clear_cache(key=None):
    """
    Clear cache for a specific key or all keys

    Args:
        key: Cache key to clear, or None to clear all
    """
    global _cache
    if key:
        if key in _cache:
            del _cache[key]
            logger.info(f"Cleared cache for '{key}'")
    else:
        _cache = {}
        logger.info("Cleared all cache")
