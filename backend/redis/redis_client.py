import os
import redis.asyncio as redis
from fastapi import Request
from redis.asyncio import Redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

async def create_redis_client():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

async def get_redis(request: Request) -> Redis:
    return request.app.state.redis
