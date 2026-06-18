from sanic import Blueprint, json
from sqlalchemy import select

from app.db import async_session
from app.models.payment import Payment
from app.middleware.auth import auth_required

payments_bp = Blueprint("payments", url_prefix="/api")


@payments_bp.get("/payments")
@auth_required
async def list_payments(request):
    async with async_session() as session:
        result = await session.execute(
            select(Payment).where(Payment.user_id == request.ctx.user_id)
        )
        payments = result.scalars().all()

    data = [
        {
            "id": p.id,
            "transaction_id": p.transaction_id,
            "account_id": p.account_id,
            "amount": str(p.amount),
        }
        for p in payments
    ]
    return json(data)
