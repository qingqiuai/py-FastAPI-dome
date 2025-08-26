from pydantic import BaseModel, Field
from typing import List

class LoadRequest(BaseModel):
    order_id: str
    customer_name: str
    customer_phone: str
    customer_addr: str

class LoadResponseItem(BaseModel):
    barcode: str
    item_id: str