from fastapi import APIRouter, Depends

from backend.api.services.status import get_status
from backend.api.services.auth import get_current_user


router = APIRouter()

@router.get("/status")
async def get_system_status(current_user: str = Depends(get_current_user)):
    return await get_status()