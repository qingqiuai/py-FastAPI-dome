### 修改：补 ForeignKey、img_path 长度、server_default
from sqlalchemy import (
    Column, Integer, String, DateTime, Enum, Text, Boolean,
    ForeignKey, func
)
from sqlalchemy.orm import declarative_base, relationship
import enum
# from datetime import timezone

Base = declarative_base()

class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"

    @classmethod
    def to_chinese(cls, value: "OrderStatus") -> str:
        return {
            cls.PENDING: "待装车",
            cls.IN_TRANSIT: "运输中",
            cls.DELIVERED: "已交付",
        }[value]

class CargoOrder(Base):
    __tablename__ = "cargo_order"
    id = Column(String(16), primary_key=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    customer_addr = Column(Text, nullable=False)
    total_qty = Column(Integer, default=0)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )
    items = relationship(
        "CargoItem",
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

class CargoItem(Base):
    __tablename__ = "cargo_item"
    id = Column(String(16), primary_key=True)
    order_id = Column(
        String(16),
        ForeignKey("cargo_order.id", ondelete="CASCADE"),
        index=True,
    )
    serial_no = Column(Integer)
    barcode = Column(String, unique=True, index=True)
    img_path = Column(String(512))
    delivered = Column(Boolean, default=False)
    order = relationship("CargoOrder", back_populates="items")