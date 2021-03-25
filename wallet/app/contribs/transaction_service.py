import json
import uuid
from decimal import Decimal
from typing import Optional, Literal, Any, Dict

from aio_pika import Connection, DeliveryMode, Message
from pydantic import validator
from pydantic.main import BaseModel

from app.core.config import settings


class TransactionInputValidate(BaseModel):
    transaction_type: Literal["TRANSFER", "REFILL"]
    transfer_wallet_id: Optional[int] = None

    @validator("transaction_type", pre=True)
    def validate_transfer_wallet_id(cls, v: Optional[int], values: Dict[str, Any]) -> int:
        if values.get("transaction_type") == "TRANSFER" and v is None:
            raise ValueError("transfer_wallet_id is required if transaction_type is Transfer")
        return v


async def send_transaction_queue(
        rabbitmq: Connection, *,
        wallet_id,
        amount: Decimal,
        transaction_type: Literal["TRANSFER", "REFILL"],
        transfer_wallet_id: Optional[int] = None
):
    TransactionInputValidate(
        transaction_type=transaction_type,
        transfer_wallet_id=transfer_wallet_id
    )
    u = uuid.uuid4()
    channel = await rabbitmq.channel()
    data = {
        "uuid": str(u),
        "wallet_id": wallet_id,
        "amount": str(amount),
        "transaction_type": transaction_type,
        "transfer_wallet_id": transfer_wallet_id
    }
    message = Message(
        json.dumps(data).encode("utf-8"),
        delivery_mode=DeliveryMode.PERSISTENT
    )
    await channel.default_exchange.publish(
        message, routing_key=settings.RABBITMQ_QUEUE_NAME
    )
    return u
