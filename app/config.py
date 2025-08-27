### 新增：自动创建目录、读取 .env、统一常量
from pathlib import Path
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()  # 读取 .env

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = Path(os.getenv("STATIC_DIR", BASE_DIR / "static")).resolve()
LOG_DIR = Path(os.getenv("LOG_DIR", BASE_DIR / "logs")).resolve()

# 若不存在则创建
STATIC_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./cargo_dev.db")

# 日志
logger.add(
    LOG_DIR / "app.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    enqueue=True,  # 异步安全
)