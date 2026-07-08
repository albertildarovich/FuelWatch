from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.database import get_db
from app.models.station import GasStation, FuelType, StationFuelPrice
from app.schemas.station import GasStationRead, GasStationWithPrices, FuelTypeRead

router = APIRouter()


@router.get("/", response_model=list[GasStationRead])
async def list_stations(
    city: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(GasStation).where(GasStation.is_active == True)
    if city:
        query = query.where(GasStation.city.ilike(f"%{city}%"))
    if brand:
        query = query.where(GasStation.brand.ilike(f"%{brand}%"))
    if region:
        query = query.where(GasStation.region.ilike(f"%{region}%"))
    query = query.order_by(GasStation.brand, GasStation.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/fuel-types", response_model=list[FuelTypeRead])
async def list_fuel_types(db: AsyncSession = Depends(get_db)):
    """Список типов топлива (АИ-92, АИ-95, ДТ, Газ и т.д.)"""
    result = await db.execute(select(FuelType).order_by(FuelType.id))
    return result.scalars().all()


@router.get("/{station_id}", response_model=GasStationWithPrices)
async def get_station(station_id: str, db: AsyncSession = Depends(get_db)):
    """Получить информацию об АЗС с текущими ценами"""
    query = select(GasStation).where(GasStation.id == station_id)
    result = await db.execute(query)
    station = result.scalar_one_or_none()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return station
