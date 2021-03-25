from sqlalchemy import Boolean, Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    phone_number = Column(String, unique=True, index=True)
    email = Column(String, nullable=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    wallet_id = Column(Integer, ForeignKey("wallet.id"))
    wallet = relationship("Wallet", back_populates="user")
    country_id = Column(Integer, ForeignKey("country.id"))
    country = relationship("Country", back_populates="users")
