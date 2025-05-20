from fastapi import APIRouter

from backend.api.routes import status
from backend.api.routes import files
from backend.api.routes import chat
from backend.api.routes import auth

api_router = APIRouter()

api_router.include_router(status.router, tags=["status"])
api_router.include_router(files.router, tags=["files"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(auth.router, tags=["auth"])