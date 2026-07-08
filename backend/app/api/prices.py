from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional

from app.database import get_db
from app.models.station import GasStation, FuelType, StationFuelPrice
from app.schemas.station import StationFuelPriceRead, StationFuelPriceCreate, PriceHistoryRead
from app.services.auth import AuthService

router = APIRouter()


@router.get("/", response_model=list[StationFuelPriceRead])
async def get_prices(
    city: Optional[str] = Query(None),
    fuel_type_id: Optional[int] = Query(None),
    station_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Получить текущие цены.
    Для MVP возвращаем все записи, позже — только последние по каждой АЗС+топливу
    """
    query = select(StationFuelPrice).order_by(
        StationFuelPrice.station_id,
        StationFuelPrice.fuel_type_id,
        desc(StationFuelPrice.created_at),
    )
    if station_id:
        query = query.where(StationFuelPrice.station_id == station_id)
    if fuel_type_id:
        query = query.where(StationFuelPrice.fuel_type_id == fuel_type_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/history/{station_id}/{fuel_type_id}", response_model=list[PriceHistoryRead])
async def get_price_history(
    station_id: str,
    fuel_type_id: int,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(StationFuelPrice)
        .where(
            StationFuelPrice.station_id == station_id,
            StationFuelPrice.fuel_type_id == fuel_type_id,
        )
        .order_by(desc(StationFuelPrice.created_at))
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/report", response_model=StationFuelPriceRead)
async def report_price(
    price_data: StationFuelPriceCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(AuthService.get_current_user),
):
    """
    Пользователь сообщает цену на АЗС
    """
    price = StationFuelPrice(
        station_id=price_data.station_id,
        fuel_type_id=price_data.fuel_type_id,
        price=price_data.price,
        currency=price_data.currency,
        source="user_reported",
        reported_by=current_user.id,
    )
    db.add(price)
    await db.commit()
    await db.refresh(price)
    return price
