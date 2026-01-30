"""
Payment endpoints (KKiapay)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from pydantic import BaseModel
import httpx
import hashlib
import hmac

from app.core.config import settings
from app.core.security import get_current_user
from app.database.session import get_db
from app.models import Subscription, User
from app.schemas.user import UserResponse

router = APIRouter(tags=["Payments"]) 


class KkiapayConfirmRequest(BaseModel):
    transaction_id: str
    amount_xof: int | None = None
    plan: str | None = "PREMIUM_MONTHLY"


@router.get("/payments/config")
async def get_payments_config():
    import os
    print(f"DEBUG - KKIAPAY_PUBLIC_KEY from os: {os.getenv('KKIAPAY_PUBLIC_KEY')}")
    print(f"DEBUG - KKIAPAY_PUBLIC_KEY from settings: {settings.KKIAPAY_PUBLIC_KEY}")
    return {
        "kkiapay_public_key": settings.KKIAPAY_PUBLIC_KEY,
        "premium_monthly_price_xof": settings.PREMIUM_MONTHLY_PRICE_XOF,
        "premium_yearly_price_xof": settings.PREMIUM_YEARLY_PRICE_XOF,
        "sandbox": settings.DEBUG,
    }


@router.post("/payments/kkiapay/confirm", response_model=UserResponse)
async def confirm_kkiapay_payment(
    payload: KkiapayConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Server-side verification via KKiapay API
    if not settings.KKIAPAY_PRIVATE_KEY or not settings.KKIAPAY_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment verification not configured",
        )
    try:
        base_url = "https://api.kkiapay.me" if not settings.DEBUG else "https://api-sandbox.kkiapay.me"
        url = f"{base_url}/v1/transactions/status"
        headers = {
            "X-PRIVATE-KEY": settings.KKIAPAY_PRIVATE_KEY,
            "X-SECRET-KEY": settings.KKIAPAY_SECRET,
            "Accept": "application/json",
        }
        params = {"transactionId": payload.transaction_id}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, params=params, timeout=10.0)
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment verification failed",
                )
            data = resp.json()
            if data.get("status") != "SUCCESS":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Payment not successful: {data.get('status', 'UNKNOWN')}",
                )
            # Optional: verify amount matches
            if payload.amount_xof is not None and data.get("amount") != payload.amount_xof:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Amount mismatch",
                )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment verification service unavailable",
        ) from e

    now = datetime.utcnow()

    amount = payload.amount_xof or settings.PREMIUM_MONTHLY_PRICE_XOF
    plan = payload.plan or "PREMIUM_MONTHLY"

    if plan == "PREMIUM_YEARLY":
        end_date = now + timedelta(days=365)
    else:
        end_date = now + timedelta(days=30)

    current_user.is_premium = True
    current_user.premium_expires_at = end_date
    current_user.updated_at = now

    sub = Subscription(
        user_id=current_user.id,
        plan=plan,
        status="ACTIVE",
        amount_paid_xof=amount,
        payment_method="KKIAPAY",
        transaction_id=payload.transaction_id,
        start_date=now,
        end_date=end_date,
        created_at=now,
        updated_at=now,
    )

    db.add(sub)
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.post("/payments/kkiapay/webhook")
async def kkiapay_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Webhook endpoint for KKiapay payment notifications"""
    if not settings.KKIAPAY_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook not configured",
        )
    
    # Verify webhook signature (if KKiapay sends one)
    # Implementation depends on KKiapay's webhook signature scheme
    
    body = await request.body()
    data = await request.json()
    
    transaction_id = data.get("transactionId") or data.get("transaction_id")
    status = data.get("status")
    amount = data.get("amount")
    
    if not transaction_id or status != "SUCCESS":
        return {"status": "ignored"}
    
    # Find user by transaction_id (query subscriptions table)
    result = await db.execute(
        select(Subscription).where(Subscription.transaction_id == transaction_id)
    )
    sub = result.scalar_one_or_none()
    
    if not sub:
        return {"status": "not_found"}
    
    # Update subscription status to ACTIVE if not already
    if sub.status != "ACTIVE":
        sub.status = "ACTIVE"
        sub.updated_at = datetime.utcnow()
        
        # Update user premium status
        user_result = await db.execute(select(User).where(User.id == sub.user_id))
        user = user_result.scalar_one()
        user.is_premium = True
        user.premium_expires_at = sub.end_date
        user.updated_at = datetime.utcnow()
        
        db.add(sub)
        db.add(user)
        await db.commit()
    
    return {"status": "ok"}
