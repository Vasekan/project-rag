from fastapi import APIRouter, UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_session
from backend.api.services.files import upload_files, get_files, delete_files, delete_chunks, upload_chunks
from backend.api.services.auth import get_current_user


router = APIRouter()

@router.post("/files/upload")
async def upload_file(file: UploadFile, current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await upload_files(file, session)

@router.get("/files")
async def list_uploaded_files(current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await get_files(session)

@router.delete("/files/{filename}")
async def delete_file(filename: str, current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await delete_files(filename, session)
