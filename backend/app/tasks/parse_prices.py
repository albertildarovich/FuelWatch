"""
Celery задачи для парсинга цен на топливо.
"""
from app.tasks.celery_app import celery_app
from app.database import async_session
from app.models.station import GasStation, FuelType, StationFuelPrice
from app.services.parser import FuelPriceParser

from sqlalchemy import select
from decimal import Decimal
from typing import Optional


@celery_app.task
def parse_all_stations():
    """
    Парсит цены на всех активных АЗС.
    Запускается по расписанию (beat).
    """
    import asyncio
    asyncio.run(_parse_all_stations_async())


async def _parse_all_stations_async():
    async with async_session() as session:
        result = await session.execute(
            select(GasStation).where(GasStation.is_active == True)
        )
        stations = result.scalars().all()

        for station in stations:
            try:
                await _parse_station(session, station)
            except Exception as e:
                print(f"Error parsing station {station.id}: {e}")

        await session.commit()


@celery_app.task
def parse_single_station(station_id: str):
    """
    Парсит цены на одной АЗС.
    """
    import asyncio
    asyncio.run(_parse_single_station_async(station_id))


async def _parse_single_station_async(station_id: str):
    async with async_session() as session:
        result = await session.execute(
            select(GasStation).where(GasStation.id == station_id)
        )
        station = result.scalar_one_or_none()
        if not station:
            print(f"Station {station_id} not found")
            return

        await _parse_station(session, station)
        await session.commit()


async def _parse_station(session, station: GasStation):
    """
    Парсит цены для одной АЗС.
    Для MVP просто симулирует получение цены.
    В реальности — использует FuelPriceParser.
    """
    # Получаем типы топлива
    fuel_types_result = await session.execute(select(FuelType))
    fuel_types = fuel_types_result.scalars().all()

    for fuel_type in fuel_types:
        # Имитация цены (в реальности — парсинг)
        base_price = Decimal("55.00")
        import random
        simulated_price = base_price + Decimal(str(round(random.uniform(-3, 3), 2)))

        price = StationFuelPrice(
            station_id=station.id,
            fuel_type_id=fuel_type.id,
            price=simulated_price,
            currency="RUB",
            source="parsed",
        )
        session.add(price)

    print(f"Parsed prices for {station.brand} - {station.name}")
