from fastapi import APIRouter

from app.api import alerts, auth, prices, stations

router = APIRouter()

router.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
router.include_router(stations.router, prefix="/api/stations", tags=["Stations"])
router.include_router(prices.router, prefix="/api/prices", tags=["Prices"])
router.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
