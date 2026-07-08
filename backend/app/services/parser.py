"""
Модуль для парсинга цен на топливо с сайтов АЗС.
"""
import httpx
from bs4 import BeautifulSoup
from decimal import Decimal
from typing import Optional
import re


class FuelPriceParser:
    """Базовый класс для парсера цен на топливо"""

    PARSERS = {}  # brand -> parser function

    @classmethod
    def register(cls, brand: str):
        """Декоратор для регистрации парсера по бренду АЗС"""
        def wrapper(func):
            cls.PARSERS[brand] = func
            return func
        return wrapper

    @staticmethod
    async def parse_price(url: str) -> Optional[Decimal]:
        """
        Универсальный парсер цены со страницы.
        Пытается найти число с двумя знаками после запятой — похожее на цену топлива.
        """
        try:
            async with httpx.AsyncClient(
                timeout=10.0, follow_redirects=True
            ) as client:
                response = await client.get(url)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "lxml")
                text = soup.get_text()

                # Ищем цены вида 55.90, 55,90
                prices = re.findall(r'(\d+[.,]\d{2})', text)
                # Берем первое подходящее значение (упрощенно)
                if prices:
                    return Decimal(prices[0].replace(",", "."))
                return None
        except Exception as e:
            print(f"Parse error for {url}: {e}")
            return None


# Пример регистрации парсера для конкретного бренда
@FuelPriceParser.register("Лукойл")
async def parse_lukoil(station_url: str) -> Optional[Decimal]:
    """Парсер для АЗС Лукойл"""
    return await FuelPriceParser.parse_price(station_url)


@FuelPriceParser.register("Газпромнефть")
async def parse_gazprom(station_url: str) -> Optional[Decimal]:
    """Парсер для АЗС Газпромнефть"""
    return await FuelPriceParser.parse_price(station_url)
