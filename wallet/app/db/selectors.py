from datetime import datetime
from typing import Optional, List

from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, aliased

from app.core.security import verify_password
from app.core.utils import PhoneNumber
from app.models import User, WalletTariff, Wallet, Country, Transaction


async def get_user_or_404(db: AsyncSession, user_id: int) -> User:
    query = select(User).filter(User.id == user_id).options(joinedload(User.wallet))
    result = await db.execute(query)
    return result.scalar_one()


async def get_user_by_phone(db: AsyncSession, *, phone_number: str) -> Optional[User]:
    print(f"get_user_by_phone() {str(phone_number) = }")
    query = select(User).filter(User.phone_number == str(phone_number))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def authenticate(db: AsyncSession, *, phone_number: str, raw_password: str) -> Optional[User]:
    user = await get_user_by_phone(db, phone_number=phone_number)
    if user is None:
        return user
    if not verify_password(raw_password, user.password):
        return None
    return user


async def wallet_tariffs(db: AsyncSession) -> List[WalletTariff]:
    query = select(WalletTariff)
    result = await db.execute(query)
    return result.scalars().all()


async def get_wallet(db: AsyncSession, wallet_id) -> Wallet:
    query = select(Wallet).filter(Wallet.id == wallet_id).options(joinedload(Wallet.wallettariff))
    result = await db.execute(query)
    return result.scalar_one()


async def get_wallet_by_phone(db: AsyncSession, phone_number: PhoneNumber):
    query = select(Wallet).\
        join(Wallet.user).\
        options(joinedload(Wallet.wallettariff), joinedload(Wallet.user)).\
        filter(User.phone_number == str(phone_number))
    result = await db.execute(query)
    return result.scalar_one()


async def get_countries(db: AsyncSession) -> List[Country]:
    query = select(Country)
    result = await db.execute(query)
    return result.scalars().all()


async def get_country_by_iso_code(db: AsyncSession, iso_code: str) -> Country:
    query = select(Country).filter(Country.iso_code == iso_code)
    result = await db.execute(query)
    return result.scalar_one()


async def transaction_by_date_range(
        db, *,
        wallet_id: int,
        start: datetime,
        end: datetime
) -> List[Transaction]:
    talias = aliased(Transaction)
    query = select(Transaction).join(
        Transaction.transfer_transaction.of_type(talias)
    ).options(joinedload(Transaction.transfer_transaction)).filter(
        or_(Transaction.wallet_id == wallet_id, talias.wallet_id == wallet_id)
    ).filter(
        Transaction.created_at >= start,
        Transaction.created_at < end
    )
    result = await db.execute(query)
    return result.scalars().all()
