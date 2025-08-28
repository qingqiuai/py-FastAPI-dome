from typing import Dict, Set

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app import crud
from app.schemas import DeliverRequest

router = APIRouter(tags=["Deliver"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/deliver")
async def deliver_items(
    req: DeliverRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, int]:
    """
    扫码模式：条码自带 customer_code，后端自动解析
    清点模式：前端下拉选客户后，把 customer_code 作为可选 query 参数
    这里统一做校验并标记交付
    """
    # 1. 查询所有待交付货物
    from app.models import CargoItem
    stmt = select(CargoItem).where(CargoItem.id.in_(req.item_ids))
    rows = (await db.execute(stmt)).scalars().all()
    if not rows:
        raise HTTPException(404, "货物不存在")

    # 2. 从条码里统一解析 customer_code
    customer_codes: Set[str] = set()
    for item in rows:
        try:
            _, code, _ = item.barcode.split("-", 2)
            customer_codes.add(code)
        except ValueError:
            raise HTTPException(400, f"条码 {item.barcode} 格式非法")
    if len(customer_codes) > 1:
        raise HTTPException(409, "一次只能交付同一客户的货物")
    customer_code = customer_codes.pop()

    # 3. 标记已交付
    updated = await crud.mark_items_delivered(db, req.item_ids)
    if updated == 0:
        raise HTTPException(409, "全部或部分货物已交付")

    return {"ok": True, "count": updated, "customer_code": customer_code}