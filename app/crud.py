# app/crud.py
import uuid
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from app.models import CargoOrder, CargoItem


# ---------- Order ----------
async def create_order(
    session: AsyncSession,
    customer_name: str,
    customer_phone: str,
    customer_addr: str,
    total_qty: int = 0,
) -> CargoOrder:
    order = CargoOrder(
        id=uuid.uuid4().hex,
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_addr=customer_addr,
        total_qty=total_qty,
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


async def get_order(session: AsyncSession, order_id: str) -> CargoOrder | None:
    res = await session.execute(select(CargoOrder).where(CargoOrder.id == order_id))
    return res.scalar_one_or_none()


# ---------- Item ----------
async def create_items_bulk(
    session: AsyncSession,
    order_id: str,
    barcodes: list[str],
) -> Sequence[CargoItem]:
    items = [
        CargoItem(
            id=uuid.uuid4().hex,
            order_id=order_id,
            serial_no=idx + 1,
            barcode=code,
        )
        for idx, code in enumerate(barcodes)
    ]
    session.add_all(items)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise
    return items


async def mark_items_delivered(
    session: AsyncSession, item_ids: list[str]
) -> None:
    await session.execute(
        update(CargoItem)
        .where(CargoItem.id.in_(item_ids))
        .values(delivered=True)
    )
    await session.commit()