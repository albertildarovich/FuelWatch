"""
Celery задачи для проверки и отправки уведомлений о ценах.
"""
from datetime import datetime, timezone

from app.tasks.celery_app import celery_app
from app.database import async_session
from app.models.alert import PriceAlert
from app.models.station import StationFuelPrice

from sqlalchemy import select, desc


@celery_app.task
def check_and_send_alerts():
    """
    Проверяет все активные уведомления и отправляет,
    если цена достигла целевого значения.
    """
    import asyncio
    asyncio.run(_check_alerts_async())


async def _check_alerts_async():
    async with async_session() as session:
        # Получаем все активные алерты
        result = await session.execute(
            select(PriceAlert).where(PriceAlert.is_active == True)
        )
        alerts = result.scalars().all()

        for alert in alerts:
            # Получаем последнюю цену по этому типу топлива
            query = (
                select(StationFuelPrice)
                .where(StationFuelPrice.fuel_type_id == alert.fuel_type_id)
                .order_by(desc(StationFuelPrice.created_at))
                .limit(1)
            )
            if alert.station_id:
                query = query.where(
                    StationFuelPrice.station_id == alert.station_id
                )

            price_result = await session.execute(query)
            latest_price = price_result.scalar_one_or_none()

            if latest_price and latest_price.price <= alert.max_price:
                # Цель достигнута — отправляем уведомление
                alert.last_notified_at = datetime.now(timezone.utc)
                alert.is_active = False  # Отключаем после срабатывания
                
                print(
                    f"ALERT: Цена {latest_price.price} руб. достигла цели "
                    f"{alert.max_price} руб. для alert {alert.id}"
                )
                # TODO: реальная отправка email/telegram
                await session.commit()

        print(f"Checked {len(alerts)} alerts")
