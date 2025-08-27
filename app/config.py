# app/config.py
from pathlib import Path
from loguru import logger
import os

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./cargo_dev.db")

# 日志
logger.add(
    BASE_DIR / "logs" / "app.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
)