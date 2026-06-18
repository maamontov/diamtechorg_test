from sanic import Blueprint, json
from sqlalchemy import select

from app.db import async_session
from app.models.account import Account
from app.middleware.auth import auth_required

accounts_bp = Blueprint("accounts", url_prefix="/api")


@accounts_bp.get("/accounts")
@auth_required
async def list_accounts(request):
    async with async_session() as session:
        result = await session.execute(
            select(Account).where(Account.user_id == request.ctx.user_id)
        )
        accounts = result.scalars().all()

    data = [
        {"id": acc.id, "balance": str(acc.balance)}
        for acc in accounts
    ]
    return json(data)
