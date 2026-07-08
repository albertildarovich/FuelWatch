import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    String, Numeric, DateTime, ForeignKey, Boolean, Integer, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    fuel_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fuel_types.id"), nullable=False
    )
    max_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    station_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("gas_stations.id"), nullable=True
    )
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_by_email: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_by_telegram: Mapped[bool] = mapped_column(Boolean, default=False)
    last_notified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="alerts")

    def __repr__(self):
        return f"<PriceAlert(id={self.id}, fuel_type={self.fuel_type_id}, max_price={self.max_price})>"
