from fastapi.responses import JSONResponse
from fastapi.requests import Request
from pydantic import ValidationError
from sqlalchemy.orm.exc import NoResultFound


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(exc.errors(), status_code=400)


async def does_not_exist_handler(request: Request, exc: NoResultFound) -> JSONResponse:
    return JSONResponse({"detail": str(exc)}, status_code=404)
