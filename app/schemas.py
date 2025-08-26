# app/schemas.py
from pydantic import BaseModel, Field
from typing import List

# 请求
class LoadRequest(BaseModel):
    order_id: str
    customer_name: str
    customer_phone: str
    customer_addr: str

class DeliverRequest(BaseModel):
    item_ids: List[str]

# 响应
class LoadResponseItem(BaseModel):
    barcode: str
    item_id: str

class OrderOut(BaseModel):
    id: str
    customer_name: str
    customer_phone: str
    customer_addr: str
    total_qty: int
    status: str
    created_at: str