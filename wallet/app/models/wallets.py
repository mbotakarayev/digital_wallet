from sqlalchemy import Column, DateTime, Integer, Numeric, String, ForeignKey, select
from sqlalchemy.orm import relationship

from app.core.utils import utc_now
from app.db.base_class import Base


class WalletTariff(Base):
    id = Column(Integer, primary_key=True, index=True)
    balance_limit = Column(Numeric)
    price = Column(Numeric)
    one_transfer_limit = Column(Numeric)
    wallets = relationship("Wallet", back_populates="wallettariff")


class Wallet(Base):
    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Numeric, default=0.0)
    currency = Column(String(10), default="USD")

    wallet_tariff_id = Column(
        Integer,
        ForeignKey("wallettariff.id"),
        default=select(WalletTariff.id).where(WalletTariff.price == 0)
    )
    wallettariff = relationship("WalletTariff", back_populates="wallets")

    user = relationship("User", uselist=False, back_populates="wallet")
    created_at = Column(DateTime, default=utc_now)
    deadline = Column(DateTime, nullable=True, default=None)
    transactions = relationship("Transaction", back_populates="wallet")


class Transaction(Base):
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    amount = Column(Numeric)
    currency = Column(String(10), default="USD")
    created_at = Column(DateTime, default=utc_now)
    transaction_type = Column(String(50))
    wallet_id = Column(
        Integer,
        ForeignKey("wallet.id")
    )
    wallet = relationship("Wallet", back_populates="transactions")

    transfer_transaction_id = Column(
        Integer,
        ForeignKey("transaction.id"),
        nullable=True,
        default=None
    )
    transfer_transaction = relationship(
        "Transaction",
        remote_side=[id],
        uselist=False,
        backref="transfer_transaction_from"
    )
