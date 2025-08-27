# app/routers/query.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import async_session
from app import crud, schemas     # 直接用 schemas.OrderOut

router = APIRouter(tags=["Query"])

async def get_db():
    async with async_session() as session:
        yield session

@router.post("/orders/by-date", response_model=List[schemas.OrderOut])
async def query_orders_by_date(
    q: schemas.OrderQuery,
    db: AsyncSession = Depends(get_db),
):
    orders = await crud.list_orders_by_date(db, q.start, q.end)
    return [schemas.OrderOut(
        id=o.id,
        customer_name=o.customer_name,
        customer_phone=o.customer_phone,
        customer_addr=o.customer_addr,
        total_qty=o.total_qty,
        status=o.status.value,
        created_at=o.created_at,
    ) for o in orders]