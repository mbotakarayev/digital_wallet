from typing import AsyncGenerator

import jwt
from aio_pika import connect
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.core import security
from app.core.config import settings
from app.db.selectors import get_user_or_404
from app.db.session import SessionLocal


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/access-token"
)


async def get_db() -> AsyncGenerator:
    async with SessionLocal() as session:
        return session


async def get_current_user(
        db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return await get_user_or_404(db, user_id=token_data.sub)


async def get_rabbitmq() -> AsyncGenerator:
    try:
        connection = await connect(settings.RABBITMQ_URL)
        yield connection
    finally:
        await connection.close()
