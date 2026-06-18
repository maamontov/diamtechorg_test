from sanic import Blueprint, json
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db import async_session
from app.models.user import User
from app.middleware.auth import auth_required, admin_required
from app.services.auth import hash_password

users_bp = Blueprint("users", url_prefix="/api")


@users_bp.get("/users/me")
@auth_required
async def get_me(request):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == request.ctx.user_id))
        user = result.scalar_one_or_none()

    if not user:
        return json({"error": "User not found"}, status=404)

    return json({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
    })


@users_bp.get("/admin/users")
@admin_required
async def list_users(request):
    async with async_session() as session:
        result = await session.execute(
            select(User).options(selectinload(User.accounts))
        )
        users = result.scalars().all()

    data = []
    for user in users:
        data.append({
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin,
            "accounts": [
                {"id": acc.id, "balance": str(acc.balance)}
                for acc in user.accounts
            ],
        })
    return json(data)


@users_bp.post("/admin/users")
@admin_required
async def create_user(request):
    body = request.json
    if not body:
        return json({"error": "Request body required"}, status=400)

    email = body.get("email")
    password = body.get("password")
    full_name = body.get("full_name")

    if not email or not password or not full_name:
        return json({"error": "email, password, and full_name are required"}, status=400)

    async with async_session() as session:
        existing = await session.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            return json({"error": "User with this email already exists"}, status=409)

        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            is_admin=body.get("is_admin", False),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return json({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_admin": user.is_admin,
    }, status=201)


@users_bp.put("/admin/users/<user_id:int>")
@admin_required
async def update_user(request, user_id: int):
    body = request.json
    if not body:
        return json({"error": "Request body required"}, status=400)

    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return json({"error": "User not found"}, status=404)

        if "email" in body:
            user.email = body["email"]
        if "full_name" in body:
            user.full_name = body["full_name"]
        if "password" in body:
            user.password_hash = hash_password(body["password"])
        if "is_admin" in body:
            user.is_admin = body["is_admin"]

        await session.commit()
        await session.refresh(user)

    return json({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_admin": user.is_admin,
    })


@users_bp.delete("/admin/users/<user_id:int>")
@admin_required
async def delete_user(request, user_id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return json({"error": "User not found"}, status=404)

        await session.delete(user)
        await session.commit()

    return json({"message": "User deleted"})
