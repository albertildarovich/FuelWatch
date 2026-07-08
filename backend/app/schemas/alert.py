import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class PriceAlertCreate(BaseModel):
    fuel_type_id: int
    max_price: Decimal
    station_id: uuid.UUID | None = None
    city: str | None = None
    notify_by_email: bool = True
    notify_by_telegram: bool = False


class PriceAlertRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    fuel_type_id: int
    max_price: Decimal
    station_id: uuid.UUID | None
    city: str | None
    is_active: bool
    notify_by_email: bool
    notify_by_telegram: bool
    created_at: datetime

    model_config = {"from_attributes": True}
