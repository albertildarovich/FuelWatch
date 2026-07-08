import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class FuelTypeRead(BaseModel):
    id: int
    name: str
    label: str

    model_config = {"from_attributes": True}


class GasStationRead(BaseModel):
    id: uuid.UUID
    name: str
    brand: str
    address: str
    city: str
    region: str
    lat: float | None
    lon: float | None

    model_config = {"from_attributes": True}


class GasStationWithPrices(GasStationRead):
    prices: list["StationFuelPriceRead"] = []


class StationFuelPriceRead(BaseModel):
    id: uuid.UUID
    station_id: uuid.UUID
    fuel_type_id: int
    fuel_type: FuelTypeRead | None = None
    price: Decimal
    currency: str
    source: str
    created_at: datetime

    model_config = {"from_attributes": True}


class StationFuelPriceCreate(BaseModel):
    station_id: uuid.UUID
    fuel_type_id: int
    price: Decimal
    currency: str = "RUB"


class PriceHistoryRead(BaseModel):
    price: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}
