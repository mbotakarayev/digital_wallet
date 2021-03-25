import dateutil.parser
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from aio_pika import Connection
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.api import deps
from app.contribs.transaction_service import send_transaction_queue
from app.core.utils import PhoneNumber, month_days, add_month
from app.db.mutations import commit_db, set_user_tariff_wallet_service
from app.db.selectors import wallet_tariffs, get_wallet, get_wallet_by_phone, transaction_by_date_range
from app.models import User, WalletTariff, Wallet, Transaction

router = APIRouter()


@router.get("/info", response_model=schemas.UserInfoWithWallet)
async def wallet_info(
        db: AsyncSession = Depends(deps.get_db),
        user: User = Depends(deps.get_current_user)
) -> User:
    return user


@router.get("/tariffs", response_model=List[schemas.WalletTariffInfo])
async def tariffs(
        db: AsyncSession = Depends(deps.get_db),
) -> List[WalletTariff]:
    return await wallet_tariffs(db)


@router.put("/set_wallet_tariff", response_model=schemas.WalletInfo)
async def set_wallet_tariff(
        data: schemas.WalletTariffId,
        db: AsyncSession = Depends(deps.get_db),
        user: User = Depends(deps.get_current_user)
) -> User:
    tariff = await commit_db(
        db=db,
        obj_callable=set_user_tariff_wallet_service,
        kwargs={"user": user, "wallet_tariff_id": data.wallet_tariff_id}
    )
    return tariff


@router.post("/refill", response_model=schemas.WalletRefillResponse)
async def refill(
        data: schemas.WalletRefillRequest,
        db: AsyncSession = Depends(deps.get_db),
        user: User = Depends(deps.get_current_user),
        rabbitmq: Connection = Depends(deps.get_rabbitmq)
) -> Dict[str, Any]:
    wallet = await get_wallet(db, user.wallet_id)
    if Decimal(wallet.balance) + data.amount > Decimal(wallet.wallettariff.balance_limit):
        raise HTTPException(
            status_code=400,
            detail="you are over the limit"
        )
    u = await send_transaction_queue(
        rabbitmq,
        wallet_id=wallet.id,
        amount=data.amount,
        transaction_type="REFILL",
    )
    return {"uuid": u}


@router.get("/get_by_phone/{phone_number}", response_model=schemas.WalletInfo)
async def wallet_by_phone(
        phone_number: str,
        db: AsyncSession = Depends(deps.get_db),
        user: User = Depends(deps.get_current_user),
) -> Wallet:
    phone_number = PhoneNumber.from_string(f"+{phone_number}")
    wallet = await get_wallet_by_phone(db, phone_number)
    print(f"wallet_by_phone()-{wallet}")
    return wallet


@router.post("/transfer", response_model=schemas.WalletRefillResponse)
async def transfer(
        data: schemas.WalletTransferRequest,
        db: AsyncSession = Depends(deps.get_db),
        user: User = Depends(deps.get_current_user),
        rabbitmq: Connection = Depends(deps.get_rabbitmq)
) -> Dict[str, Any]:
    wallet = await get_wallet(db, user.wallet_id)
    if wallet.id == user.wallet.id:
        raise HTTPException(
            status_code=400,
            detail="can't transfer to self wallet"
        )
    if data.amount > Decimal(wallet.wallettariff.one_transfer_limit):
        raise HTTPException(
            status_code=400,
            detail="you are over the one transfer limit"
        )
    u = await send_transaction_queue(
        rabbitmq,
        wallet_id=wallet.id,
        amount=data.amount,
        transaction_type="REFILL",
    )
    return {"uuid": u}


#  Не правильое решение
@router.post("/notify_transaction", response_model=schemas.WalletRefillResponse)
async def notify_transaction(
        data: schemas.WalletRefillResponse,
        db: AsyncSession = Depends(deps.get_db),
) -> Dict[str, Any]:
    return data.dict()


@router.get("/transaction_history", response_model=List[schemas.Transaction])
async def transaction_history(
        date_range: Optional[str] = None,
        db: AsyncSession = Depends(deps.get_db),
        user: User = Depends(deps.get_current_user)
) -> List[Transaction]:
    if date_range is None:
        today = datetime.today()
        start = datetime(year=today.year, month=today.month, day=1)
        end = add_month(start, 1)
        date_range = ",".join([str(start), str(end)])
    start, end = date_range.split(",")
    start, end = dateutil.parser.parse(start), dateutil.parser.parse(end)
    transactions = await transaction_by_date_range(
        db, start=start, end=end, wallet_id=user.wallet_id
    )
    print(transactions)
    return transactions
