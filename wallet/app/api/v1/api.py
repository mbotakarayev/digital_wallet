from fastapi import APIRouter

from app.api.v1.endpoints import auth, wallets, users, settings

api_router = APIRouter()
api_router.include_router(wallets.router, prefix="/wallets", tags=["wallets"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
