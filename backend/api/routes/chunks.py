from fastapi import APIRouter, UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_session
from backend.api.services.files import upload_files, get_files, delete_files, delete_chunks, upload_chunks
from backend.api.services.auth import get_current_user


router = APIRouter()


@router.post("/chunks/{filename}")
async def upload_file_ai(filename: str, current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await upload_chunks(filename, current_user, session)

@router.delete("/chunks/{filename}")
async def delete_from_ai(filename: str, current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await delete_chunks(filename, current_user, session)