from typing import Optional, TypeVar, Callable, Union, List, Any, Tuple, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.base_class import Base
from app.models import User, Wallet

_M = TypeVar("_M", bound=Base)


async def commit_db(
        db: AsyncSession,
        *,
        obj_callable: Callable,
        args: Optional[Union[List[Any], Tuple[Any, ...]]] = None,
        kwargs: Optional[Dict[str, Any]] = None
) -> _M:
    args, kwargs = args or [], kwargs or {}
    obj = await obj_callable(*args, **kwargs)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def add_user(
        *,
        full_name: str,
        phone_number: str,
        raw_password: str,
        is_active: bool,
        country_id: int,
        email: Optional[str] = None
) -> User:
    password = get_password_hash(raw_password)
    return User(
        full_name=full_name,
        phone_number=str(phone_number),
        password=password,
        is_active=is_active,
        email=email,
        country_id=country_id,
        wallet=Wallet()
    )


async def update_user(
        user, *,
        full_name: str,
        email: str,
        raw_password: str
) -> User:
    password = get_password_hash(raw_password)
    user.password = password
    user.full_name = full_name
    user.email = email
    return user


async def set_user_tariff_wallet_service(user, *, wallet_tariff_id: int) -> Wallet:
    wallet = user.wallet
    wallet.wallet_tariff_id = wallet_tariff_id
    return wallet
