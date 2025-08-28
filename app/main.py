### 修改：重命名避免遮蔽 & 显式 lifespan 使用
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import load, transport, deliver, orders
from app.exceptions import register_exception_handlers
from app.config import STATIC_DIR

@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期控制"""
    await init_db()
    yield

fastapi_app = FastAPI(title="Cargo API", lifespan=lifespan)

# CORS
fastapi_app.add_middleware(
    CORSMiddleware,     # type: ignore[arg-type]
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# static
fastapi_app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# routers
fastapi_app.include_router(load.router, prefix="/api", tags=["装车"])
fastapi_app.include_router(transport.router, prefix="/api", tags=["运输"])
fastapi_app.include_router(deliver.router, prefix="/api", tags=["交付"])
fastapi_app.include_router(orders.router, prefix="/api", tags=["订单"])

# exception
register_exception_handlers(fastapi_app)

# 导出 ASGI 入口名仍为 app
app = fastapi_app