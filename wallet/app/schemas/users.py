from typing import Optional

from pydantic import BaseModel, EmailStr

from app.core.utils import PhoneNumber
from app.schemas.wallets import WalletInfo


class UserBase(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None


class UserWithUsername(UserBase):
    phone_number: PhoneNumber


class UserInfo(UserWithUsername):
    id: int

    class Config:
        orm_mode = True


class UserInfoWithWallet(UserWithUsername):
    wallet: WalletInfo

    class Config:
        orm_mode = True


class PasswordMixin(BaseModel):
    password: str


class CreateUser(PasswordMixin, UserBase):
    country_code: int
    country_iso_code: str
    phone_number: PhoneNumber
    is_active: Optional[bool] = True


class UpdateUser(PasswordMixin, UserBase):
    pass
