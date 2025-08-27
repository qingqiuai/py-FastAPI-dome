# app/routers/load.py
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import async_session
from app import crud, schemas

router = APIRouter(tags=["Load"])

async def get_db():
    async with async_session() as session:
        yield session


@router.post("/load", response_model=List[schemas.LoadResponseItem])
async def load_cargo(
    req: schemas.LoadRequest,          # JSON 参数
    img: UploadFile = File(...),      # 只上传 1 张图
    db: AsyncSession = Depends(get_db),
):
    """
    1. 根据 req.total_qty 生成条码
    2. 同一张图片保存到 static/<barcode>.jpg
    3. 返回条码列表
    """
    # 1. 创建订单
    order = await crud.create_order(
        db,
        customer_name=req.customer_name,
        customer_phone=req.customer_phone,
        customer_addr=req.customer_addr,
        total_qty=req.total_qty,
    )

    # 2. 按 total_qty 生成条码
    barcodes = [f"{order.id}-{idx+1:04d}" for idx in range(req.total_qty)]
    items = await crud.create_items_bulk(db, order.id, barcodes)

    # 3. 把同一张图片写入每一条货物记录
    content = await img.read()
    for item in items:
        img_path = f"static/{item.barcode}.jpg"
        with open(img_path, "wb") as f:
            f.write(content)

    return [schemas.LoadResponseItem(barcode=i.barcode, item_id=i.id) for i in items]