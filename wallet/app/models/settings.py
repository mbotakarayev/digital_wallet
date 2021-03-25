from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Country(Base):
    id = Column(Integer, primary_key=True, index=True)
    iso_code = Column(String(5), unique=True)
    country_code = Column(Integer)
    users = relationship("User", back_populates="country")
