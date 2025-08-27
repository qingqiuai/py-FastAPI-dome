# app/routers/load.py
import aiofiles
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app import crud, schemas
from app.config import STATIC_DIR

router = APIRouter(tags=["Load"])

async def get_db():
    async with async_session() as session:
        yield session

@router.post("/load", response_model=list[schemas.LoadResponseItem])
async def load_cargo(
    req: schemas.LoadRequest,
    img: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if req.total_qty <= 0:
        raise HTTPException(400, "total_qty must be > 0")

    # 1. 创建订单
    order = await crud.create_order(
        db,
        customer_name=req.customer_name,
        customer_phone=req.customer_phone,
        customer_addr=req.customer_addr,
        total_qty=req.total_qty,
    )

    # 2. 生成条码
    barcodes = [f"{order.id}-{idx+1:04d}" for idx in range(req.total_qty)]
    items = await crud.create_items_bulk(db, order.id, barcodes)

    # 3. 异步保存同一张图片
    STATIC_DIR.mkdir(exist_ok=True)
    img_path = STATIC_DIR / f"{order.id}.jpg"
    async with aiofiles.open(img_path, "wb") as f:
        await f.write(await img.read())

    # 4. 记录路径
    for item in items:
        item.img_path = str(img_path)
    await db.commit()

    return [schemas.LoadResponseItem(barcode=i.barcode, item_id=i.id) for i in items]