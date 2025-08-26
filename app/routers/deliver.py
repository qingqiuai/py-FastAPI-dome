import uuid
import os
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import async_session
from app.models import CargoItem

router = APIRouter(tags=["deliver"])

UPLOAD_DIR = "static"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class DeliverResult(BaseModel):
    ok: bool
    message: str
    remain: int
    delivered: int
    total: int


@router.post("/deliver", response_model=DeliverResult)
async def deliver(
    mode: str = Form(...),                  # scan / count
    customer_code: str = Form(...),
    barcodes: List[str] = Form([]),
    total_qty: int = Form(None),
    file: UploadFile = File(...),
    sign: UploadFile = File(...),
    db: AsyncSession = Depends(lambda: async_session()),
):
    order_id = datetime.now(timezone.utc).strftime("%Y%m%d")

    # 1. 当天该客户全部 & 已交付件数
    total = await db.scalar(
        select(func.count(CargoItem.id))
        .where(CargoItem.order_id == order_id, CargoItem.customer_code == customer_code)
    )
    delivered = await db.scalar(
        select(func.count(CargoItem.id))
        .where(
            CargoItem.order_id == order_id,
            CargoItem.customer_code == customer_code,
            CargoItem.delivered == True,
        )
    )
    remain = (total or 0) - (delivered or 0)

    # 2. 根据模式确定待交付条码
    if mode == "scan":
        if not barcodes:
            return DeliverResult(ok=False, message="扫码模式必须提供条码", remain=remain, delivered=delivered, total=total)
        target_items = await db.execute(
            select(CargoItem)
            .where(
                CargoItem.order_id == order_id,
                CargoItem.customer_code == customer_code,
                CargoItem.barcode.in_(barcodes),
                CargoItem.delivered == False,
            )
        )
        target_items = target_items.scalars().all()
        if len(target_items) != len(barcodes):
            return DeliverResult(
                ok=False,
                message=f"系统显示剩余 {remain} 件，您输入 {len(barcodes)} 件，请重新确认",
                remain=remain,
                delivered=delivered,
                total=total,
            )
        qty = len(target_items)

    elif mode == "count":
        if total_qty is None or total_qty <= 0:
            return DeliverResult(ok=False, message="清点模式必须提供正整数件数", remain=remain, delivered=delivered, total=total)
        if remain != total_qty:
            return DeliverResult(
                ok=False,
                message=f"系统显示剩余 {remain} 件，您输入 {total_qty} 件，请重新确认",
                remain=remain,
                delivered=delivered,
                total=total,
            )
        target_items = await db.execute(
            select(CargoItem)
            .where(
                CargoItem.order_id == order_id,
                CargoItem.customer_code == customer_code,
                CargoItem.delivered == False,
            )
        )
        target_items = target_items.scalars().all()
        qty = len(target_items)
    else:
        return DeliverResult(ok=False, message="mode 只能是 scan 或 count", remain=remain, delivered=delivered, total=total)

    # 3. 保存文件并更新状态
    photo_path = f"{UPLOAD_DIR}/{uuid.uuid4().hex}.jpg"
    sign_path = f"{UPLOAD_DIR}/{uuid.uuid4().hex}.png"
    for p, f in [(photo_path, file), (sign_path, sign)]:
        with open(p, "wb") as fp:
            fp.write(await f.read())

    ids = [i.id for i in target_items]
    await db.execute(
        update(CargoItem)
        .where(CargoItem.id.in_(ids))
        .values(delivered=True, delivered_img=photo_path, sign_img=sign_path)
    )
    await db.commit()

    return DeliverResult(
        ok=True,
        message="交付完成",
        remain=0,
        delivered=delivered + qty,
        total=total,
    )