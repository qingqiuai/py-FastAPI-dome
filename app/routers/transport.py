
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session
from app.models import CargoOrder, OrderStatus
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
# from fastapi import APIRouter, HTTPException
# from app.sms import send_sms  # 伪代码，真实项目再实现

router = APIRouter(tags=["transport"])

@router.post("/depart")
async def depart(
    # customer_name: str = Form(...),
    db: AsyncSession = Depends(lambda: async_session()),
):
    order_id = datetime.now(timezone.utc).strftime("%Y%m%d")
    res = await db.execute(
        select(CargoOrder).where(CargoOrder.id == order_id)
    )
    order = res.scalar_one_or_none()
    if not order:
        raise HTTPException(404, "当日订单不存在")

    order.status = OrderStatus.运输中
    await db.commit()

    # 发短信（可选）
    # send_sms(order.customer_phone, "货物已发车，请注意收货")
    return {"detail": "已发车", "order_id": order_id}