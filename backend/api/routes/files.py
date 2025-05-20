from fastapi import APIRouter, UploadFile, Depends

from backend.api.services.files import upload_files, get_files, delete_files
from backend.api.services.auth import get_current_user


router = APIRouter()

@router.post("/files/upload")
async def upload_file(file: UploadFile, current_user: str = Depends(get_current_user)):
    return await upload_files(file)

@router.get("/files")
async def list_uploaded_files(current_user: str = Depends(get_current_user)):
    return await get_files()

@router.delete("/files/{filename}")
async def delete_file(filename: str, current_user: str = Depends(get_current_user)):
    return await delete_files(filename)
