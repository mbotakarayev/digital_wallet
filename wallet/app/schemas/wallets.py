from datetime import datetime
from decimal import Decimal
from typing import Optional, ForwardRef

from pydantic import BaseModel, UUID4


class WalletTariffInfo(BaseModel):
    id: int
    balance_limit: Decimal
    price: Decimal
    one_transfer_limit: Decimal

    class Config:
        orm_mode = True


class WalletTariffId(BaseModel):
    wallet_tariff_id: int


class WalletBase(BaseModel):
    balance: Decimal
    currency: str
    created_at: datetime
    deadline: Optional[datetime]
    wallet_tariff_id: int


class WalletInfo(WalletBase):
    id: int

    class Config:
        orm_mode = True


class WalletRefillResponse(BaseModel):
    uuid: UUID4


class WalletRefillRequest(BaseModel):
    channel: str
    amount: Decimal


class WalletTransferRequest(WalletRefillRequest):
    transfer_wallet_id: int


Transaction = ForwardRef("Transaction")


class Transaction(BaseModel):
    id: int
    amount: Decimal
    currency: str
    created_at: datetime
    transaction_type: str
    wallet_id: int
    transfer_transaction: Transaction = None

    class Config:
        orm_mode = True


Transaction.update_forward_refs()
