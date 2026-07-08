"""
Скрипт для заполнения БД начальными данными:
- Типы топлива
- Крупные сети АЗС (Москва и МО для начала)
"""
import asyncio
import random
from decimal import Decimal

from sqlalchemy import select, func

from app.database import async_session
from app.database import engine, Base
from app.models.station import GasStation, FuelType, StationFuelPrice
from app.models.user import User
from app.services.auth import AuthService


STATIONS_DATA = [
    # Москва
    {"name": "Лукойл №1", "brand": "Лукойл", "address": "Москва, Ленинградский пр-т, 1",
     "city": "Москва", "region": "Москва", "lat": 55.7558, "lon": 37.6173},
    {"name": "Лукойл №2", "brand": "Лукойл", "address": "Москва, ул. Тверская, 10",
     "city": "Москва", "region": "Москва", "lat": 55.7658, "lon": 37.6073},
    {"name": "Газпромнефть №1", "brand": "Газпромнефть", "address": "Москва, Кутузовский пр-т, 20",
     "city": "Москва", "region": "Москва", "lat": 55.7458, "lon": 37.5773},
    {"name": "Газпромнефть №2", "brand": "Газпромнефть", "address": "Москва, МКАД 45-й км",
     "city": "Москва", "region": "Москва", "lat": 55.8758, "lon": 37.7173},
    {"name": "Роснефть №1", "brand": "Роснефть", "address": "Москва, пр-т Мира, 100",
     "city": "Москва", "region": "Москва", "lat": 55.7958, "lon": 37.6373},
    {"name": "Shell №1", "brand": "Shell", "address": "Москва, Ленинский пр-т, 50",
     "city": "Москва", "region": "Москва", "lat": 55.7158, "lon": 37.5673},
    {"name": "Татнефть №1", "brand": "Татнефть", "address": "Москва, Варшавское шоссе, 30",
     "city": "Москва", "region": "Москва", "lat": 55.6458, "lon": 37.6473},
    # Санкт-Петербург
    {"name": "Лукойл №3", "brand": "Лукойл", "address": "СПб, Невский пр-т, 50",
     "city": "Санкт-Петербург", "region": "Санкт-Петербург", "lat": 59.9343, "lon": 30.3351},
    {"name": "Газпромнефть №3", "brand": "Газпромнефть", "address": "СПб, наб. Фонтанки, 10",
     "city": "Санкт-Петербург", "region": "Санкт-Петербург", "lat": 59.9243, "lon": 30.3151},
    {"name": "Роснефть №2", "brand": "Роснефть", "address": "СПб, пр-т Энгельса, 150",
     "city": "Санкт-Петербург", "region": "Санкт-Петербург", "lat": 60.0143, "lon": 30.3651},
    # Нижний Новгород
    {"name": "Лукойл №4", "brand": "Лукойл", "address": "НН, ул. Б. Покровская, 1",
     "city": "Нижний Новгород", "region": "Нижегородская область", "lat": 56.3269, "lon": 44.0075},
    {"name": "Газпромнефть №4", "brand": "Газпромнефть", "address": "НН, пр-т Гагарина, 30",
     "city": "Нижний Новгород", "region": "Нижегородская область", "lat": 56.2969, "lon": 43.9875},
]

FUEL_TYPES = [
    {"name": "a-92", "label": "АИ-92"},
    {"name": "a-95", "label": "АИ-95"},
    {"name": "a-98", "label": "АИ-98"},
    {"name": "dt", "label": "ДТ (дизель)"},
    {"name": "gas", "label": "Газ (пропан/бутан)"},
]


async def seed_database():
    """Заполняет БД начальными данными"""
    async with async_session() as session:
        # Сначала проверяем, есть ли уже данные
        count = await session.execute(select(func.count()).select_from(FuelType))
        if count.scalar() > 0:
            print("Database already seeded, skipping...")
            return

        # Типы топлива
        for ft in FUEL_TYPES:
            fuel_type = FuelType(**ft)
            session.add(fuel_type)
        await session.flush()

        # АЗС
        for st in STATIONS_DATA:
            station = GasStation(**st)
            session.add(station)
        await session.flush()

        # Начальные цены (для демо)
        stations = (await session.execute(select(GasStation))).scalars().all()
        fuel_types = (await session.execute(select(FuelType))).scalars().all()

        base_prices = {
            "a-92": Decimal("52.50"),
            "a-95": Decimal("56.80"),
            "a-98": Decimal("62.30"),
            "dt": Decimal("59.90"),
            "gas": Decimal("24.50"),
        }

        for station in stations:
            for ft in fuel_types:
                base = base_prices.get(ft.name, Decimal("55.00"))
                variation = Decimal(str(round(random.uniform(-3, 3), 2)))
                price_val = base + variation

                price = StationFuelPrice(
                    station_id=station.id,
                    fuel_type_id=ft.id,
                    price=price_val,
                    currency="RUB",
                    source="parsed",
                )
                session.add(price)

        await session.commit()
        print(f"Seeded: {len(FUEL_TYPES)} fuel types, {len(STATIONS_DATA)} stations, prices added")

    print("✅ Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
