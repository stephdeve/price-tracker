"""
Alert endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from datetime import datetime

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.alert import Alert
from app.models.product import Product
from app.schemas.alert import AlertCreate, AlertUpdate, AlertResponse

router = APIRouter(tags=["Alerts"])


@router.post("/alerts", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new price alert
    
    Alert types:
    - **target_price**: Notify when price <= threshold_value
    - **percentage_drop**: Notify when price drops by threshold_value %
    - **prediction**: Notify when AI predicts price drop (Premium)
    - **availability**: Notify when out-of-stock item returns
    """
    # Check if product exists
    result = await db.execute(select(Product).where(Product.id == alert_data.product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produit non trouvé"
        )
    
    # Create alert
    alert = Alert(
        user_id=current_user.id,
        product_id=alert_data.product_id,
        alert_type=alert_data.alert_type,
        threshold_value=alert_data.threshold_value,
        notification_channel=alert_data.notification_channel,
        is_active=True
    )
    
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    
    return alert


@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all alerts for current user
    """
    result = await db.execute(
        select(Alert)
        .where(Alert.user_id == current_user.id)
        .order_by(Alert.created_at.desc())
    )
    alerts = result.scalars().all()
    
    # Load product relationships
    for alert in alerts:
        await db.refresh(alert, ["product"])
    
    return alerts


@router.put("/alerts/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    alert_data: AlertUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing alert
    """
    result = await db.execute(
        select(Alert).where(
            and_(
                Alert.id == alert_id,
                Alert.user_id == current_user.id
            )
        )
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerte non trouvée"
        )
    
    # Update fields
    if alert_data.alert_type is not None:
        alert.alert_type = alert_data.alert_type
    if alert_data.threshold_value is not None:
        alert.threshold_value = alert_data.threshold_value
    if alert_data.notification_channel is not None:
        alert.notification_channel = alert_data.notification_channel
    if alert_data.is_active is not None:
        alert.is_active = alert_data.is_active
    
    alert.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(alert)
    
    return alert


@router.delete("/alerts/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an alert
    """
    result = await db.execute(
        select(Alert).where(
            and_(
                Alert.id == alert_id,
                Alert.user_id == current_user.id
            )
        )
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerte non trouvée"
        )
    
    await db.delete(alert)
    await db.commit()
    
    return None


@router.post("/alerts/{alert_id}/test", status_code=status.HTTP_200_OK)
async def test_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a test notification for an alert
    """
    result = await db.execute(
        select(Alert).where(
            and_(
                Alert.id == alert_id,
                Alert.user_id == current_user.id
            )
        )
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerte non trouvée"
        )
    
    # Load product for notification
    await db.refresh(alert, ["product"])
    
    # TODO: Implement actual notification sending
    # from app.services.notifications import send_notification
    # await send_notification(current_user, alert, alert.product, test=True)
    
    return {
        "message": f"Notification test envoyée via {alert.notification_channel}",
        "alert_id": alert_id
    }
