import time
from collections import defaultdict, deque

from fastapi import HTTPException, status
from redis.asyncio import Redis

from .config import get_settings

settings = get_settings()
_memory_windows: dict[str, deque[float]] = defaultdict(deque)
_redis: Redis | None = None
_redis_unavailable = False


async def get_redis() -> Redis | None:
    global _redis, _redis_unavailable
    if _redis_unavailable and not settings.is_production:
        return None
    if _redis is None:
        try:
            candidate = Redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=0.25,
                socket_timeout=0.5,
            )
            await candidate.ping()
            _redis = candidate
        except Exception:
            if settings.is_production:
                raise RuntimeError("Redis is required in production")
            _redis_unavailable = True
            return None
    return _redis


async def close_redis() -> None:
    global _redis, _redis_unavailable
    redis = _redis
    _redis = None
    _redis_unavailable = False
    if redis is not None:
        await redis.aclose()


async def check_rate_limit(
    key: str,
    limit: int,
    window_seconds: int,
) -> None:
    redis = await get_redis()
    now = time.time()
    if redis is not None:
        bucket = int(now // window_seconds)
        redis_key = f"ratelimit:{key}:{bucket}"
        count = await redis.incr(redis_key)
        if count == 1:
            await redis.expire(redis_key, window_seconds + 2)
    else:
        timestamps = _memory_windows[key]
        cutoff = now - window_seconds
        while timestamps and timestamps[0] <= cutoff:
            timestamps.popleft()
        timestamps.append(now)
        count = len(timestamps)

    if count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": str(window_seconds)},
        )
