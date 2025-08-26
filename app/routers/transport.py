from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app import crud, models, schemas

router = APIRouter(tags=["Transport"])

async def get_db():
    async with async_session() as session:
        yield session

@router.get("/transport/{order_id}", response_model=schemas.OrderOut)
async def get_transport_status(order_id: str, db=Depends(get_db)):
    order = await crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return schemas.OrderOut(
        id=order.id,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        customer_addr=order.customer_addr,
        total_qty=order.total_qty,
        status=models.OrderStatus.to_chinese(order.status),
        created_at=order.created_at.isoformat(),
    )