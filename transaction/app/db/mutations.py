from decimal import Decimal
from typing import Literal, Callable, List, Any, Tuple, Union, Optional, Dict, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base_class import Base
from app.models.transactions import Transaction
from app.models.wallets import Wallet

_M = TypeVar("_M", bound=Base)


async def commit_db(
        db: AsyncSession,
        *,
        obj_callable: Callable,
        args: Optional[Union[List[Any], Tuple[Any, ...]]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        async_callback: Optional[Callable] = None
) -> _M:
    args, kwargs = args or [], kwargs or {}
    obj = await obj_callable(*args, **kwargs)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    if async_callback:
        await async_callback(db, obj)
    return obj


async def add_transaction(
        *,
        uuid: str,
        amount: Decimal,
        wallet_id: int,
        transaction_type: Literal["REFILL", "TRANSFER"],
        currency: str = "USD",
        transfer_transaction: Optional[Transaction] = None
) -> Transaction:
    return Transaction(
        uuid=str(uuid),
        amount=amount,
        wallet_id=wallet_id,
        transaction_type=transaction_type,
        currency=currency,
        transfer_transaction=transfer_transaction
    )


async def recalc_wallet(
        *,
        wallet: Wallet,
        amount: Decimal,
) -> Wallet:
    wallet.balance += amount
    return wallet
