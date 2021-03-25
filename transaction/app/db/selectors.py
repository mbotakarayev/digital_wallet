from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallets import Wallet


async def get_wallet(db: AsyncSession, wallet_id) -> Wallet:
    query = select(Wallet).filter(Wallet.id == wallet_id)
    result = await db.execute(query)
    return result.scalar_one()
