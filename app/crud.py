### 修改：事务边界调整、异常脱钩、返回值类型修正
import uuid
from datetime import datetime
from typing import Sequence, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError

from app.models import CargoOrder, CargoItem
from app.exceptions import BarcodeDuplicateError

# ---------- Order ----------
async def create_order(
    session: AsyncSession,
    customer_name: str,
    customer_phone: str,
    customer_addr: str,
    total_qty: int = 0,
) -> CargoOrder:
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
    res = await session.execute(delete(CargoOrder).where(CargoOrder.id == order_id))
    return res.rowcount > 0

# ---------- Item ----------
async def create_items_bulk(
    session: AsyncSession,
    order_id: str,
    barcodes: List[str],
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
    session.add_all(items)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise BarcodeDuplicateError() from exc
    return items

async def mark_items_delivered(session: AsyncSession, item_ids: List[str]) -> int:
    res = await session.execute(
        update(CargoItem)
        .where(CargoItem.id.in_(item_ids), CargoItem.delivered.is_(False))
        .values(delivered=True)
    )
    return res.rowcount