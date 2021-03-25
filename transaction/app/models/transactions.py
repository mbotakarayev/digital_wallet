from datetime import datetime

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Transaction(Base):
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    amount = Column(Numeric)
    currency = Column(String(10), default="USD")
    created_at = Column(DateTime, default=datetime.utcnow)
    transaction_type = Column(String(50))
    wallet_id = Column(Integer)
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
