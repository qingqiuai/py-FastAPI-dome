# app/exceptions.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from loguru import logger

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(IntegrityError)
    async def integrity_handler(request: Request, exc: IntegrityError):
        logger.error(f"DB IntegrityError: {exc}")
        return JSONResponse(
            status_code=409,
            content={"detail": "数据冲突，请检查"},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        logger.error(f"ValueError: {exc}")
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )