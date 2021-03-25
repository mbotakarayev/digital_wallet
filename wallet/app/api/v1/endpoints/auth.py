from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, Form
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm as BaseOAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.db.mutations import add_user, commit_db
from app.db.selectors import authenticate, get_user_by_phone, get_country_by_iso_code
from app.models import User

router = APIRouter()


class OAuth2PasswordRequestForm(BaseOAuth2PasswordRequestForm):
    def __init__(
            self,
            username: str = Form(...),
            password: str = Form(...),
            scope: str = Form("")
    ):
        super(OAuth2PasswordRequestForm, self).__init__(
            username=username,
            password=password,
            scope=scope,
        )


@router.post("/sign-up", response_model=schemas.UserInfo)
async def signup(data: schemas.CreateUser, db: AsyncSession = Depends(deps.get_db)) -> User:
    user = await get_user_by_phone(db, phone_number=data.phone_number)
    if user is not None:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists"
        )
    country = await get_country_by_iso_code(db, data.country_iso_code)
    user = await commit_db(db=db, obj_callable=add_user, kwargs={
        "full_name": data.full_name,
        "phone_number": data.phone_number,
        "raw_password": data.password,
        "is_active": data.is_active,
        "email": data.email,
        "country_id": country.id
    })
    return user


@router.post("/access-token", response_model=schemas.Token)
async def access_token(
        db: AsyncSession = Depends(deps.get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
) -> Dict[str, Any]:
    user = await authenticate(db, phone_number=form_data.username, raw_password=form_data.password)
    if user is None:
        raise HTTPException(status_code=400, detail="Username or password invalid")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
