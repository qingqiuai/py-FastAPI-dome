### 修改：Pillow 校验、文件大小、条码长度、异步关闭文件
import io
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from PIL import Image
import aiofiles

from app.database import AsyncSessionLocal
from app import crud, schemas
from app.config import STATIC_DIR

router = APIRouter(tags=["Load"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/load", response_model=list[schemas.LoadResponseItem])
async def load_cargo(
    req: schemas.LoadRequest,
    img: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    # 1. 先读少量字节判断格式
    sample = await img.read(512)
    await img.seek(0)
    try:
        Image.open(io.BytesIO(sample)).verify()
    except Exception:
        raise HTTPException(400, "请上传有效 jpeg/png 图片")

    # 2. 总大小（Pillow 不验证，手动读取）
    try:
        contents = await img.read()
    finally:
        await img.seek(0)  # ← 确保后续再读能拿到数据
        await img.close()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(413, "图片超过 5 MB")

    # 3. 创建订单
    order = await crud.create_order(
        db,
        customer_name=req.customer_name,
        customer_phone=req.customer_phone,
        customer_addr=req.customer_addr,
        total_qty=req.total_qty,
    )

    # 4. 生成条码
    customer_code = req.customer_code  # ← 前端/后台给
    barcodes = [
        f"{order.id}-{customer_code}-{idx + 1:03d}"
        for idx in range(req.total_qty)
    ]
    items = await crud.create_items_bulk(db, order.id, barcodes)

    # 5. 保存图片
    suffix = Path(img.filename).suffix or ".jpg"
    img_path = STATIC_DIR / f"{order.id}{suffix}"
    async with aiofiles.open(img_path, "wb") as f:
        await f.write(contents)

    # 6. 更新路径
    for item in items:
        item.img_path = str(img_path.relative_to(STATIC_DIR.parent))
    await db.commit()

    return [schemas.LoadResponseItem(barcode=i.barcode, item_id=i.id) for i in items]