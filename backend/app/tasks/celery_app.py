from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "fuelwatch",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.parse_prices",
        "app.tasks.send_alerts",
    ],
)

# Настройка расписания
celery_app.conf.beat_schedule = {
    "parse-all-stations-every-4-hours": {
        "task": "app.tasks.parse_prices.parse_all_stations",
        "schedule": crontab(minute=0, hour=f"*/{settings.parse_interval_hours}"),
    },
    "check-alerts-after-parse": {
        "task": "app.tasks.send_alerts.check_and_send_alerts",
        "schedule": crontab(minute=5, hour=f"*/{settings.parse_interval_hours}"),
    },
}

celery_app.conf.timezone = "Europe/Moscow"
