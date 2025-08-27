# app/routers/orders.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List

from app.database import async_session
from app import crud
from app.schemas import OrderOut

router = APIRouter(tags=["Orders"])

async def get_db():
    async with async_session() as session:
        yield session


# ---------- 1. 分页查询（POST + body） ----------
from pydantic import BaseModel

class OrderQueryBody(BaseModel):
    start: datetime
    end: datetime
    limit: int = 100
    offset: int = 0


@router.post("/orders/search", response_model=List[OrderOut])
async def search_orders(
    body: OrderQueryBody,
    db: AsyncSession = Depends(get_db),
):
    orders = await crud.list_orders_by_date(
        db, body.start, body.end, body.limit, body.offset
    )
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


# ---------- 2. 删除订单 ----------
@router.delete("/orders/{order_id}")
async def delete_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
):
    ok = await crud.delete_order(db, order_id)
    if not ok:
        raise HTTPException(404, "订单不存在")
    return {"ok": True}


# ---------- 3. 修改订单 ----------
@router.patch("/orders/{order_id}", response_model=OrderOut)
async def update_order(
    order_id: str,
    payload: dict,
    db: AsyncSession = Depends(get_db),
):
    allowed = {"customer_name", "customer_phone", "customer_addr"}
    payload = {k: v for k, v in payload.items() if k in allowed}
    if not payload:
        raise HTTPException(400, "无可更新字段")

    order = await crud.get_order(db, order_id)
    if not order:
        raise HTTPException(404, "订单不存在")

    for k, v in payload.items():
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