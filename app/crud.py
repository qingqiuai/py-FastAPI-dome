import uuid
from datetime import datetime
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
# from loguru import logger
from app.models import CargoOrder, CargoItem

# ---------- Order ----------
async def create_order(
    session: AsyncSession,
    customer_name: str,
    customer_phone: str,
    customer_addr: str,
    total_qty: int = 0,
) -> CargoOrder:
    async with session.begin():
        order = CargoOrder(
            id=uuid.uuid4().hex[:16],
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_addr=customer_addr,
            total_qty=total_qty,
        )
        session.add(order)
        await session.flush()
        return order

async def get_order(session: AsyncSession, order_id: str) -> CargoOrder | None:
    res = await session.execute(select(CargoOrder).where(CargoOrder.id == order_id))
    return res.scalar_one_or_none()

async def list_orders_by_date(
    session: AsyncSession,
    start: datetime,
    end: datetime,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[CargoOrder]:
    stmt = (
        select(CargoOrder)
        .where(CargoOrder.created_at >= start, CargoOrder.created_at <= end)
        .order_by(CargoOrder.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    res = await session.execute(stmt)
    return res.scalars().all()

async def delete_order(session: AsyncSession, order_id: str) -> bool:
    async with session.begin():
        res = await session.execute(delete(CargoOrder).where(CargoOrder.id == order_id))
        return bool(res.rowcount) > 0

# ---------- Item ----------
async def create_items_bulk(
    session: AsyncSession,
    order_id: str,
    barcodes: list[str],
) -> Sequence[CargoItem]:
    items = [
        CargoItem(
            id=uuid.uuid4().hex[:16],
            order_id=order_id,
            serial_no=idx + 1,
            barcode=code,
        )
        for idx, code in enumerate(barcodes)
    ]
    try:
        async with session.begin_nested():
            session.add_all(items)
    except IntegrityError as e:
        await session.rollback()
        from http.client import HTTPException
        raise HTTPException(409, "条码已存在") from e
    return items

async def mark_items_delivered(
    session: AsyncSession, item_ids: list[str]
) -> int:
    async with session.begin():
        res = await session.execute(
            update(CargoItem)
            .where(CargoItem.id.in_(item_ids), CargoItem.delivered.is_(False))
            .values(delivered=True)
        )
        return bool(res.rowcount)