from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.api import deps
from app.db.selectors import get_countries
from app.models import User
from app.schemas import Country

router = APIRouter()


@router.get("counties", response_model=List[schemas.Country])
async def countries(
        db: AsyncSession = Depends(deps.get_db),
        user: User = Depends(deps.get_current_user)  # noqa
) -> List[Country]:
    return await get_countries(db)
