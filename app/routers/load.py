import uuid,os
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models import CargoOrder, CargoItem
from app.schemas import LoadResponseItem

router = APIRouter(tags=["load"])

UPLOAD_DIR = "static"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/load", response_model=List[LoadResponseItem])
async def load_cargo(
    customer_name: str = Form(...),
    customer_phone: str = Form(...),
    customer_addr: str = Form(...),
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(lambda: async_session()),
):
    # 1. 固定日批次
    order_id = datetime.now(timezone.utc).strftime("%Y%m%d")

    # 2. 创建或复用 CargoOrder
    res = await db.execute(select(CargoOrder).where(CargoOrder.id == order_id))
    cargo_order = res.scalar_one_or_none()
    if not cargo_order:
        cargo_order = CargoOrder(
            id=order_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_addr=customer_addr,
            total_qty=len(files),
        )
        db.add(cargo_order)
    else:
        cargo_order.total_qty += len(files)

    # 3. 计算该客户当天已存在的条数，续接序号
    existing_count = await db.scalar(
        select(func.count(CargoItem.id))
        .where(
            CargoItem.order_id == order_id,
            CargoItem.customer_code == customer_name,
        )
    )
    serial_start = (existing_count or 0) + 1

    # 4. 逐张照片处理
    out = []
    for idx, file in enumerate(files, serial_start):
        barcode = f"{order_id}{customer_name[:4]}{idx:03d}"
        file_name = f"{uuid.uuid4().hex}.jpg"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        item = CargoItem(
            id=str(uuid.uuid4()),
            order_id=order_id,
            customer_code=customer_name,
            serial_no=idx,
            barcode=barcode,
            loaded_img=file_path,
        )
        db.add(item)
        out.append(LoadResponseItem(barcode=barcode, item_id=item.id))

    await db.commit()
    return out


@router.get("/today_customers")
async def today_customers(db: AsyncSession = Depends(lambda: async_session())):
    """返回今天已经收过货的客户名称列表"""
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    codes = await db.execute(
        select(CargoItem.customer_code)
        .where(CargoItem.order_id == today)
        .distinct()
        .order_by(CargoItem.customer_code)
    )
    return codes.scalars().all()