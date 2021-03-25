from sqlalchemy import Integer, Column, Numeric

from app.db.base_class import Base


class Wallet(Base):
    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Numeric, default=0.0)
