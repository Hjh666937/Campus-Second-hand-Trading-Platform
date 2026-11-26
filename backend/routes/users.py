import os
import uuid

from flask import Blueprint, current_app, g, request
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from models import Item, Review, User
from utils.auth import require_login
from utils.response import fail, ok

users_bp = Blueprint("users", __name__, url_prefix="/api/users")

GENDERS = {"male", "female", "secret"}
ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
NICKNAME_MIN, NICKNAME_MAX = 2, 12
CAMPUS_MIN, CAMPUS_MAX = 2, 20
PASSWORD_MIN, PASSWORD_MAX = 6, 20


def _clean(value):
    return value.strip() if isinstance(value, str) else ""


@users_bp.get("/me")
@require_login
def me():
    """返回当前登录用户信息，用于前端刷新页面后恢复登录态。"""
    return ok(g.current_user.to_public_dict())


@users_bp.put("/me")
@require_login
def update_me():
    """修改昵称、校区、性别。学号、信用分、角色不允许自行修改。"""
    payload = request.get_json(silent=True) or {}
    user = g.current_user

    if "nickname" in payload:
        nickname = _clean(payload.get("nickname"))
        if not (NICKNAME_MIN <= len(nickname) <= NICKNAME_MAX):
            return fail(f"昵称需 {NICKNAME_MIN}-{NICKNAME_MAX} 个字", 422)
        user.nickname = nickname

    if "campus" in payload:
        campus = _clean(payload.get("campus"))
        if not (CAMPUS_MIN <= len(campus) <= CAMPUS_MAX):
            return fail(f"校区需 {CAMPUS_MIN}-{CAMPUS_MAX} 个字", 422)
        user.campus = campus

    if "gender" in payload:
        gender = _clean(payload.get("gender"))
        if gender not in GENDERS:
            return fail("性别参数不合法", 422)
        user.gender = gender

    db.session.commit()
    return ok(user.to_public_dict(), message="资料已更新")


@users_bp.put("/me/password")
@require_login
def change_password():
    """修改登录密码：需校验当前密码。"""
    payload = request.get_json(silent=True) or {}
    user = g.current_user

    old_password = payload.get("oldPassword")
    new_password = payload.get("newPassword")
    if not isinstance(old_password, str) or not isinstance(new_password, str):
        return fail("请输入当前密码和新密码", 422)

    try:
        valid = check_password_hash(user.password_hash, old_password)
    except (ValueError, TypeError):
        valid = False
    if not valid:
        return fail("当前密码不正确", 400)

    if not (PASSWORD_MIN <= len(new_password) <= PASSWORD_MAX):
        return fail(f"新密码需 {PASSWORD_MIN}-{PASSWORD_MAX} 位", 422)
    if new_password == old_password:
        return fail("新密码不能与当前密码相同", 422)

    user.password_hash = generate_password_hash(new_password)
    user.must_change_password = False
    db.session.commit()
    return ok(message="密码已修改")


def _build_seller_profile(owners):
    """按用户列表生成卖家主页数据（昵称可能重名，id 路由只传一个）。"""
    owner = owners[0]
    owner_ids = [row.id for row in owners]
    items_query = Item.query.filter(
        Item.seller_id.in_(owner_ids), Item.is_deleted == False
    )
    on_sale_items = (
        items_query.filter(Item.status == "on_sale")
        .order_by(Item.created_at.desc(), Item.id.desc())
        .all()
    )
    sold_count = items_query.filter(Item.status == "sold").count()

    reviews = (
        Review.query.filter(Review.target_id.in_(owner_ids))
        .order_by(Review.created_at.desc(), Review.id.desc())
        .all()
    )
    total_rating = sum(row.rating for row in reviews)
    rating = round(total_rating / len(reviews), 1) if reviews else 5

    return {
        "id": owner.id,
        "nickname": owner.nickname,
        "avatar": owner.avatar,
        "campus": owner.campus or "",
        "credit": owner.credit,
        "rating": rating,
        "reviewCount": len(reviews),
        "onSaleCount": len(on_sale_items),
        "soldCount": sold_count,
        "items": [item.to_card_dict() for item in on_sale_items],
        "reviews": [row.to_dict() for row in reviews],
    }


@users_bp.get("/id/<int:user_id>")
def seller_profile_by_id(user_id):
    """卖家主页（按用户 id，避免同名账号数据混在一起）。"""
    owner = db.session.get(User, user_id)
    if not owner:
        return fail("该用户不存在", 404)
    return ok(_build_seller_profile([owner]))


@users_bp.get("/<nickname>")
def seller_profile(nickname):
    """卖家主页：公开资料 + 在售/已售统计 + 在售商品 + 交易评价。"""
    nickname = _clean(nickname)
    owners = User.query.filter_by(nickname=nickname).all()
    if not owners:
        return fail("该用户不存在", 404)
    return ok(_build_seller_profile(owners))


@users_bp.post("/me/avatar")
@require_login
def upload_avatar():
    """上传头像，保存到 uploads/avatars，返回可访问的 URL。"""
    file = request.files.get("file")
    if not file or not file.filename:
        return fail("请选择图片", 422)

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_IMAGE_EXT:
        return fail("仅支持 JPG / PNG / WebP 格式", 422)

    folder = os.path.join(current_app.config["UPLOAD_DIR"], "avatars")
    os.makedirs(folder, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    file.save(os.path.join(folder, filename))

    url = f"{request.host_url.rstrip('/')}/uploads/avatars/{filename}"
    g.current_user.avatar = url
    db.session.commit()
    return ok({"avatarUrl": url}, message="头像已更新")
