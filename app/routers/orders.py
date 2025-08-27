### 修改：GET 分页查询、PatchOrder schema、软删除标记
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app import crud
from app.schemas import OrderOut, PatchOrder

router = APIRouter(tags=["Orders"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/orders", response_model=List[OrderOut])
async def search_orders(
    start: datetime = Query(...),
    end: datetime = Query(...),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    orders = await crud.list_orders_by_date(db, start, end, limit, offset)
    return [
        OrderOut(
            id=o.id,
            customer_name=o.customer_name,
            customer_phone=o.customer_phone,
            customer_addr=o.customer_addr,
            total_qty=o.total_qty,
            status=o.status.value,
            created_at=o.created_at,
        )
        for o in orders
    ]

@router.delete("/orders/{order_id}")
async def delete_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
):
    ok = await crud.delete_order(db, order_id)
    if not ok:
        raise HTTPException(404, "订单不存在")
    return {"ok": True}

@router.patch("/orders/{order_id}", response_model=OrderOut)
async def update_order(
    order_id: str,
    payload: PatchOrder,
    db: AsyncSession = Depends(get_db),
):
    order = await crud.get_order(db, order_id)
    if not order:
        raise HTTPException(404, "订单不存在")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(order, k, v)
    await db.commit()
    await db.refresh(order)

    return OrderOut(
        id=order.id,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        customer_addr=order.customer_addr,
        total_qty=order.total_qty,
        status=order.status.value,
        created_at=order.created_at,
    )