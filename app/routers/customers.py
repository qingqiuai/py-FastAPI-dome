from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, distinct

from app.database import AsyncSessionLocal
from app.models import CargoItem

router = APIRouter(tags=["Customers"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/today_customers")
async def today_customers(
    db: AsyncSession = Depends(get_db),
) -> List[str]:
    """
    清点模式专用：返回今天所有出现的客户代码
    """
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    stmt = (
        select(distinct(CargoItem.barcode))
        .where(CargoItem.created_at >= start, CargoItem.created_at < end)
    )
    barcodes = (await db.execute(stmt)).scalars().all()

    # 从条码提取 customer_code
    return list({bc.split("-")[1] for bc in barcodes if bc.count("-") >= 2})