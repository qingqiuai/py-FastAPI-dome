### 新增：PatchOrder、PaginatedOrders
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional

class LoadRequest(BaseModel):
    order_id: str
    customer_name: str
    customer_phone: str
    customer_addr: str
    total_qty: int = Field(gt=0)

class DeliverRequest(BaseModel):
    item_ids: List[str]

class LoadResponseItem(BaseModel):
    barcode: str
    item_id: str

class OrderQueryBody(BaseModel):
    start: datetime
    end: datetime
    limit: int = Field(100, le=1000)
    offset: int = Field(0, ge=0)

class OrderOut(BaseModel):
    id: str
    customer_name: str
    customer_phone: str
    customer_addr: str
    total_qty: int
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PatchOrder(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_addr: Optional[str] = None

class PaginatedOrders(BaseModel):
    total: int
    items: List[OrderOut]