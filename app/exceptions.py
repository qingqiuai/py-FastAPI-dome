### 修改：用 '_' 占位 & 记录日志
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, NoResultFound
from pydantic import ValidationError
from loguru import logger

class BarcodeDuplicateError(ValueError):
    pass

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(IntegrityError)
    async def integrity_handler(_request: Request, exc: IntegrityError) -> JSONResponse:
        logger.error("IntegrityError caught: {}", exc)
        return JSONResponse(status_code=409, content={"detail": "数据冲突，请检查"})

    @app.exception_handler(ValidationError)
    async def validation_handler(_request: Request, exc: ValidationError) -> JSONResponse:
        logger.error("ValidationError caught: {}", exc)
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(NoResultFound)
    async def notfound_handler(_request: Request, _exc: NoResultFound) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": "记录不存在"})

    @app.exception_handler(BarcodeDuplicateError)
    async def barcode_dup_handler(_request: Request, _exc: BarcodeDuplicateError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": "条码已存在"})

    @app.exception_handler(Exception)
    async def all_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error")
        return JSONResponse(status_code=500, content={"detail": "服务器开小差了"})