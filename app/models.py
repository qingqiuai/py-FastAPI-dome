# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
import enum, datetime

Base = declarative_base()

class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"          # 待装车
    IN_TRANSIT = "IN_TRANSIT"    # 运输中
    DELIVERED = "DELIVERED"      # 已交付

    @classmethod
    def to_chinese(cls, value: "OrderStatus") -> str:
        return {
            cls.PENDING: "待装车",
            cls.IN_TRANSIT: "运输中",
            cls.DELIVERED: "已交付",
        }[value]

class CargoOrder(Base):
    __tablename__ = "cargo_order"
    id = Column(String(16), primary_key=True)      # 短 ID
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    customer_addr = Column(Text, nullable=False)
    total_qty = Column(Integer, default=0)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

Index("idx_order_created", CargoOrder.created_at)

class CargoItem(Base):
    __tablename__ = "cargo_item"
    id = Column(String(16), primary_key=True)
    order_id = Column(String(16), index=True)
    serial_no = Column(Integer)
    barcode = Column(String, unique=True, index=True)
    img_path = Column(String)
    delivered = Column(Boolean, default=False)