from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import async_session
from app import crud, schemas

router = APIRouter(tags=["Load"])

# 依赖：获取 DB Session
async def get_db():
    async with async_session() as session:
        yield session

@router.post("/load", response_model=List[schemas.LoadResponseItem])
async def load_cargo(
    req: schemas.LoadRequest,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    创建订单并批量生成货物条码
    - 使用 UUID 保证 order_id 唯一
    - 一次性插入所有 CargoItem，减少往返
    """
    # 1. 创建订单
    order = await crud.create_order(
        db,
        customer_name=req.customer_name,
        customer_phone=req.customer_phone,
        customer_addr=req.customer_addr,
        total_qty=len(files),
    )

    # 2. 生成条码 & 写入 CargoItem
    barcodes = [f"{order.id}-{idx+1:04d}" for idx in range(len(files))]
    items = await crud.create_items_bulk(db, order.id, barcodes)

    # 3. 保存上传图片（这里仅演示保存到本地 static）
    for idx, file in enumerate(files):
        content = await file.read()
        img_path = f"static/{items[idx].id}.jpg"
        with open(img_path, "wb") as f:
            f.write(content)

    return [schemas.LoadResponseItem(barcode=i.barcode, item_id=i.id) for i in items]