import asyncio
import logging
import pika
import time
import uuid

from aio_pika import connect, IncomingMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.contrib.api_clients.wallets import WalletAPIClient
from app.core.config import settings
from app.db.mutations import commit_db, add_transaction, recalc_wallet
from app.db.selectors import get_wallet
from app.db.session import SessionLocal
from app.models.transactions import Transaction
from app.models.wallets import Wallet

# logger = logging.getLogger(__name__)
loop = asyncio.get_event_loop()


async def after_transaction_create(db: AsyncSession, obj: Transaction) -> None:
    async with WalletAPIClient() as wallet:
        await wallet.notify_transaction(uuid=obj.uuid)
    await confirm_transaction(db, obj)


async def confirm_transaction(db: AsyncSession, obj: Transaction) -> Wallet:
    wallet = await get_wallet(db, wallet_id=obj.wallet_id)
    wallet = await commit_db(db, obj_callable=recalc_wallet, kwargs={
        "wallet": wallet,
        "amount": obj.amount
    })
    return wallet


async def handle_consume(message: IncomingMessage) -> None:
    async with message.process():
        print(f"{message.body = }")
        data = schemas.TransactionInputSchemas.parse_raw(message.body)
        async with SessionLocal() as session:
            transaction = await commit_db(session, obj_callable=add_transaction, kwargs={
                "uuid": data.uuid,
                "amount": data.amount,
                "wallet_id": data.wallet_id,
                "transaction_type": data.transaction_type,
                "currency": data.currency,
            }, async_callback=after_transaction_create)
            if data.transaction_type == schemas.TransactionType.TRANSFER:
                await commit_db(session, obj_callable=add_transaction, kwargs={
                    "uuid": uuid.uuid4(),
                    "amount": data.amount,
                    "wallet_id": data.transfer_wallet_id,
                    "transaction_type": data.transaction_type,
                    "currency": data.currency,
                    "transfer_transaction": transaction
                }, async_callback=after_transaction_create)


async def main():
    logging.debug(f"---------{settings.RABBITMQ_URL.path = }")
    connection = await connect(settings.RABBITMQ_URL, loop=loop)
    channel = await connection.channel()

    queue = await channel.declare_queue(
        settings.RABBITMQ_QUEUE_NAME,
        durable=True
    )
    await queue.consume(handle_consume)


if __name__ == "__main__":
    print("------------", settings.RABBITMQ_URL.path)
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_URL.host,
        port=settings.RABBITMQ_URL.port,
        credentials=pika.PlainCredentials(
            settings.RABBITMQ_URL.user,
            settings.RABBITMQ_URL.password
        )
    )
    while True:
        try:
            c = pika.BlockingConnection(parameters)
            if c.is_open:
                print('OK')
                c.close()
                break
        except Exception as error:
            print('No connection yet:', error.__class__.__name__)
            time.sleep(5)

    print("start application")
    loop = asyncio.get_event_loop()
    loop.create_task(main())

    print("Press CTRL+C to exit")
    loop.run_forever()
