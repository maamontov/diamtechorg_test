import hashlib
from decimal import Decimal, InvalidOperation

from sanic import Blueprint, json
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db import async_session
from app.models.account import Account
from app.models.payment import Payment
from app.models.user import User
from app.config import WEBHOOK_SECRET_KEY

webhook_bp = Blueprint("webhook", url_prefix="/api/webhook")


def verify_signature(data: dict) -> bool:
    account_id = str(data.get("account_id", ""))
    amount = str(data.get("amount", ""))
    transaction_id = str(data.get("transaction_id", ""))
    user_id = str(data.get("user_id", ""))

    raw = f"{account_id}{amount}{transaction_id}{user_id}{WEBHOOK_SECRET_KEY}"
    expected = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return data.get("signature") == expected


@webhook_bp.post("/payment")
async def payment_webhook(request):
    body = request.json
    if not body:
        return json({"error": "Request body required"}, status=400)

    required_fields = ["transaction_id", "account_id", "user_id", "amount", "signature"]
    for field in required_fields:
        if field not in body:
            return json({"error": f"Missing field: {field}"}, status=400)

    if not verify_signature(body):
        return json({"error": "Invalid signature"}, status=400)

    transaction_id = body["transaction_id"]
    account_id = body["account_id"]
    user_id = body["user_id"]
    try:
        amount = Decimal(str(body["amount"]))
    except InvalidOperation:
        return json({"error": "Invalid amount"}, status=400)

    if not amount.is_finite():
        return json({"error": "Invalid amount"}, status=400)

    async with async_session() as session:
        try:
            async with session.begin():
                existing = await session.execute(
                    select(Payment).where(Payment.transaction_id == transaction_id)
                )
                if existing.scalar_one_or_none():
                    return json({"error": "Transaction already processed"}, status=409)

                result_user = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = result_user.scalar_one_or_none()
                if not user:
                    return json({"error": "User not found"}, status=404)

                result_acc = await session.execute(
                    select(Account)
                    .where(Account.id == account_id, Account.user_id == user_id)
                    .with_for_update()
                )
                account = result_acc.scalar_one_or_none()

                if not account:
                    account = Account(user_id=user_id, balance=Decimal("0"))
                    session.add(account)
                    await session.flush()
                    account_id = account.id

                account.balance += amount

                payment = Payment(
                    transaction_id=transaction_id,
                    account_id=account_id,
                    user_id=user_id,
                    amount=amount,
                )
                session.add(payment)
        except IntegrityError:
            return json({"error": "Transaction already processed"}, status=409)

    return json({"status": "ok"}, status=200)
