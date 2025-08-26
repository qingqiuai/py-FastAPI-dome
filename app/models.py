from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
import enum, datetime

Base = declarative_base()

class OrderStatus(str, enum.Enum):
    待装车 = "待装车"
    运输中 = "运输中"
    已交付 = "已交付"

class CargoOrder(Base):
    __tablename__ = "cargo_order"
    id = Column(String, primary_key=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    customer_addr = Column(Text, nullable=False)
    total_qty = Column(Integer, default=0)
    status = Column(Enum(OrderStatus), default=OrderStatus.待装车)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class CargoItem(Base):
    __tablename__ = "cargo_item"
    id = Column(String, primary_key=True)
    order_id = Column(String, index=True)
    serial_no = Column(Integer)
    barcode = Column(String, unique=True, index=True)
    loaded_img = Column(String)  # 本地文件路径或 OSS URL
    customer_code = Column(String, nullable=False, default='')
    delivered = Column(Boolean, default=False)