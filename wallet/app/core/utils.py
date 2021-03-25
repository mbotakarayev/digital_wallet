from calendar import monthrange
from datetime import datetime
from typing import Optional, Any, Dict

from phonenumbers import (
    PhoneNumber as BasePhoneNumber,
    PhoneNumberFormat,
    format_number,
    parse as phone_number_parse, is_valid_number
)

from app.core.config import settings


def utc_now():
    return datetime.utcnow()


month_days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def add_month(dt: datetime, months: int) -> datetime:
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, monthrange(year, month)[1])
    return datetime(year, month, day)


class PhoneNumber(BasePhoneNumber):
    format_map = {
        "E164": PhoneNumberFormat.E164,
        "INTERNATIONAL": PhoneNumberFormat.INTERNATIONAL,
        "NATIONAL": PhoneNumberFormat.NATIONAL,
    }

    def as_e164(self):
        return format_number(self, self.format_map["E164"])

    def as_international(self):
        return format_number(self, self.format_map["INTERNATIONAL"])

    def as_national(self):
        return format_number(self, self.format_map["NATIONAL"])

    def as_msisdn(self):
        return f"{self.country_code}{self.national_number}"

    @classmethod
    def from_string(
            cls,
            phone_number: str,
            region: Optional[str] = None
    ):
        region = region or settings.COUNTRY_ISO
        print(f"-{region = }, {phone_number = }")
        new_cls = cls()
        phone_number_parse(
            phone_number,
            region=region,
            numobj=new_cls
        )
        return new_cls

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            pattenr=r"^\+(7)(77[0-9])([0-9]{7})",
            examples="+77777777777",
            type="string",
            format="phone"
        )

    @classmethod
    def validate(cls, v: str, values: Dict[str, Any]):
        region_code = values.get("country_iso_code")
        country_code = values.get("country_code")
        if country_code is not None:
            v = f"+{country_code}{v}"
        phone_number = cls.from_string(v, region_code)
        if not is_valid_number(phone_number):
            raise ValueError("not valid phone number")
        return phone_number

    def __str__(self):
        return self.as_e164()
