import redis.asyncio as redis

from app.core.config import settings

redis_pool = redis.ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)

async def get_redis_client():
    client = redis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        await client.close()
