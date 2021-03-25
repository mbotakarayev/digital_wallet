from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.api import deps
from app.db.mutations import commit_db, update_user
from app.models import User

router = APIRouter()


@router.get("/info", response_model=schemas.UserInfo)
async def user_info(
        db: AsyncSession = Depends(deps.get_db),
        user: User = Depends(deps.get_current_user)
) -> User:
    return user


@router.put("/update", response_model=schemas.UserInfo)
async def update_user_api(
        data: schemas.UpdateUser,
        db: AsyncSession = Depends(deps.get_db),
        user: User = Depends(deps.get_current_user)
) -> User:
    user = await commit_db(db=db, obj_callable=update_user, kwargs={
        "user": user,
        "full_name": data.full_name,
        "email": data.email,
        "raw_password": data.password
    })
    return user
