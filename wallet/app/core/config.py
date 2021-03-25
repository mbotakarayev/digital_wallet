import secrets

from typing import Any, Callable, Dict, List, Optional, Union, Tuple, Type

from pydantic import AnyHttpUrl, BaseSettings, validator, ValidationError, PostgresDsn, AnyUrl
from sqlalchemy.orm.exc import NoResultFound

from app import exceptions


class RabbitMQDsn(AnyUrl):
    allowed_schemes = {"amqp", "pyamqp"}
    user_required = True


class AsyncPostgresDsn(PostgresDsn):
    allowed_schemes = list(PostgresDsn.allowed_schemes) + ["postgresql+asyncpg"]


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 7 days = 7 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    SERVER_NAME: str = "wallet"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "Digit Wallets service"

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

    DEFAULT_LIMIT: float = 20000.00

    EXCEPTIONS_TO_HANDLE: List[Tuple[Type[Exception], Callable]] = [
        (ValidationError, exceptions.validation_exception_handler),
        (NoResultFound, exceptions.does_not_exist_handler),
    ]

    JWT_ALGORITHM: str = "HS256"

    RABBITMQ_URL: RabbitMQDsn = "amqp://guest:guest@localhost/"
    RABBITMQ_QUEUE_NAME: str = "TRANSACTION"

    COUNTRY_ISO: str = "CY"

    class Config:
        case_sensitive = True


settings = Settings()
