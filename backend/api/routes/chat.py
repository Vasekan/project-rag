from fastapi import APIRouter, Depends

from backend.api.services.chat import get_answer
from backend.api.services.auth import get_current_user
from backend.api.schemas.chat import ChatBaseSchema


router = APIRouter()

@router.post("/chat")
async def chat(message: ChatBaseSchema, current_user: str = Depends(get_current_user)):
    return await get_answer(message, current_user)