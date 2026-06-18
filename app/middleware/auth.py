from functools import wraps

from sanic import json
import jwt

from app.services.auth import decode_token


def get_token(request) -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


def auth_required(f):
    @wraps(f)
    async def decorated(request, *args, **kwargs):
        token = get_token(request)
        if not token:
            return json({"error": "Missing authentication token"}, status=401)
        try:
            payload = decode_token(token)
            request.ctx.user_id = payload["user_id"]
            request.ctx.is_admin = payload["is_admin"]
        except jwt.ExpiredSignatureError:
            return json({"error": "Token expired"}, status=401)
        except jwt.InvalidTokenError:
            return json({"error": "Invalid token"}, status=401)
        return await f(request, *args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    async def decorated(request, *args, **kwargs):
        token = get_token(request)
        if not token:
            return json({"error": "Missing authentication token"}, status=401)
        try:
            payload = decode_token(token)
            request.ctx.user_id = payload["user_id"]
            request.ctx.is_admin = payload["is_admin"]
            if not payload["is_admin"]:
                return json({"error": "Admin access required"}, status=403)
        except jwt.ExpiredSignatureError:
            return json({"error": "Token expired"}, status=401)
        except jwt.InvalidTokenError:
            return json({"error": "Invalid token"}, status=401)
        return await f(request, *args, **kwargs)
    return decorated
