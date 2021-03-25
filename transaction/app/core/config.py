import requests
from typing import Optional, Dict, Any

from pydantic import BaseSettings, HttpUrl, AnyUrl, validator, PostgresDsn


class RabbitMQDsn(AnyUrl):
    allowed_schemes = {"amqp", "pyamqp"}
    user_required = True


def check_services_url(v: str) -> str:
    resp = requests.options(v)
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        if 500 <= exc.response.status_code < 599:
            raise ValueError(exc.response.text)
    return v


class AsyncPostgresDsn(PostgresDsn):
    allowed_schemes = list(PostgresDsn.allowed_schemes) + ["postgresql+asyncpg"]


class Settings(BaseSettings):
    RABBITMQ_URL: RabbitMQDsn = "amqp://guest:guest@localhost:5672/"
    RABBITMQ_QUEUE_NAME: str = "TRANSACTION"
    WALLET_SERVICE_BASE: str = "http://127.0.0.1:8005/"

    _check_wallet_services_url = validator("WALLET_SERVICE_BASE", pre=True)(check_services_url)

    POSTGRES_SERVER: str = "127.0.0.1"
    POSTGRES_USER: str = "digit_wallet"
    POSTGRES_PASSWORD: str = "digit_wallet"
    POSTGRES_DB: str = "digit_wallet"
    SQLALCHEMY_DATABASE_URI: Optional[AsyncPostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return AsyncPostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )


settings = Settings()
