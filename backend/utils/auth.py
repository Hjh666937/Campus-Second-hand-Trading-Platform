from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, request

from extensions import db
from models import User
from utils.response import fail


def create_token(user, days):
    """签发 JWT。payload 只放用户 id，角色和封禁状态每次请求查库获取。"""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "iat": now,
        "exp": now + timedelta(days=days),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def require_login(view):
    """校验 Authorization: Bearer <token>，通过后把用户放进 g.current_user。"""

    @wraps(view)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return fail("请先登录", 401)

        token = header[len("Bearer "):].strip()
        try:
            payload = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return fail("登录已过期，请重新登录", 401)
        except jwt.InvalidTokenError:
            return fail("登录凭证无效，请重新登录", 401)

        user = db.session.get(User, int(payload["sub"]))
        if not user:
            return fail("用户不存在", 401)
        if user.status != "active":
            return fail("账号已被封禁，请联系管理员", 403)

        g.current_user = user
        return view(*args, **kwargs)

    return wrapper


def require_admin(view):
    """在 require_login 基础上要求 role=admin。"""

    @wraps(view)
    @require_login
    def wrapper(*args, **kwargs):
        if g.current_user.role != "admin":
            return fail("需要管理员权限", 403)
        return view(*args, **kwargs)

    return wrapper


def optional_login():
    """不强制登录，但如果带了有效 token 就解析到 g.current_user。

    用于公开页面需要知道"当前查看者是否有权限看下架商品"这类场景。
    """
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        token = header[len("Bearer "):].strip()
        try:
            payload = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            user = db.session.get(User, int(payload["sub"]))
            if user and user.status == "active":
                g.current_user = user
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError):
            pass
