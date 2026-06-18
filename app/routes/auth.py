from sanic import Blueprint, json
from sqlalchemy import select

from app.db import async_session
from app.models.user import User
from app.services.auth import verify_password, create_token

auth_bp = Blueprint("auth", url_prefix="/api/auth")


@auth_bp.post("/login")
async def login(request):
    body = request.json
    if not body:
        return json({"error": "Request body required"}, status=400)

    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        return json({"error": "Email and password required"}, status=400)

    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        return json({"error": "Invalid email or password"}, status=401)

    token = create_token(user.id, user.is_admin)
    return json({"token": token})
