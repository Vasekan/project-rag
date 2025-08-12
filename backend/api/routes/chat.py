from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from backend.api.services.chat import get_answer, get_messages
from backend.api.services.auth import get_current_user
from backend.api.schemas.chat import ChatBaseSchema
from backend.redis.redis_client import get_redis


router = APIRouter()

@router.post("/chat")
async def chat(message: ChatBaseSchema, current_user: str = Depends(get_current_user), redis: Redis = Depends(get_redis)):
    return await get_answer(message, current_user, redis)

@router.get("/messages")
async def get_message(current_user: str = Depends(get_current_user), redis: Redis = Depends(get_redis)):
    return await get_messages(current_user, redis)