from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app import crud, schemas

router = APIRouter(tags=["Deliver"])

async def get_db():
    async with async_session() as session:
        yield session

@router.post("/deliver")
async def deliver_items(req: schemas.DeliverRequest, db=Depends(get_db)):
    await crud.mark_items_delivered(db, req.item_ids)
    return {"ok": True}