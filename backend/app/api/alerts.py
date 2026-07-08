from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.alert import PriceAlert
from app.schemas.alert import PriceAlertCreate, PriceAlertRead
from app.services.auth import AuthService

router = APIRouter()


@router.post("/", response_model=PriceAlertRead, status_code=201)
async def create_alert(
    alert_data: PriceAlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(AuthService.get_current_user),
):
    alert = PriceAlert(
        user_id=current_user.id,
        fuel_type_id=alert_data.fuel_type_id,
        max_price=alert_data.max_price,
        station_id=alert_data.station_id,
        city=alert_data.city,
        notify_by_email=alert_data.notify_by_email,
        notify_by_telegram=alert_data.notify_by_telegram,
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


@router.get("/", response_model=list[PriceAlertRead])
async def list_alerts(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(AuthService.get_current_user),
):
    result = await db.execute(
        select(PriceAlert).where(PriceAlert.user_id == current_user.id)
    )
    return result.scalars().all()


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(AuthService.get_current_user),
):
    result = await db.execute(
        select(PriceAlert).where(
            PriceAlert.id == alert_id,
            PriceAlert.user_id == current_user.id,
        )
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    await db.delete(alert)
    await db.commit()
    return {"message": "Alert deleted"}
