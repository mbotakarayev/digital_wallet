from decimal import Decimal
from enum import Enum
from typing import Literal, Any, Dict, Optional

from pydantic import BaseModel, UUID4, validator


class TransactionType(str, Enum):
    REFILL: str = "REFILL"
    TRANSFER: str = "TRANSFER"

    def __str__(self) -> str:
        return self.value


class TransactionInputSchemas(BaseModel):
    uuid: UUID4
    transaction_type: Literal["REFILL", "TRANSFER"]
    amount: Decimal
    wallet_id: int
    currency: str = "USD"
    transfer_wallet_id: Optional[int]

    @validator("transaction_type")
    def validate_transfer_wallet_id(cls, v: Optional[int], values: Dict[str, Any]) -> int:
        return v

    @validator("amount")
    def validate_amount(cls, v: Decimal, values: Dict[str, Any]) -> Decimal:
        print(f"validate_amount {values = }")
        if values["transaction_type"] == TransactionType.TRANSFER:
            v = -v
        return v
