from flask import Blueprint, g, request

from extensions import db
from models import Favorite, Item
from utils.auth import require_login
from utils.response import fail, ok

favorites_bp = Blueprint("favorites", __name__, url_prefix="/api/favorites")


@favorites_bp.post("", strict_slashes=False)
@require_login
def toggle_favorite():
    """收藏 / 取消收藏，返回最新状态。"""
    payload = request.get_json(silent=True) or {}
    try:
        item_id = int(payload.get("itemId"))
    except (TypeError, ValueError):
        return fail("请选择商品", 422)

    item = Item.query.filter(Item.id == item_id, Item.is_deleted == False).first()
    if not item:
        return fail("商品不存在或已删除", 404)

    row = Favorite.query.filter_by(
        user_id=g.current_user.id, item_id=item.id
    ).first()
    if row:
        db.session.delete(row)
        db.session.commit()
        return ok({"favorite": False}, message="已取消收藏")

    db.session.add(Favorite(user_id=g.current_user.id, item_id=item.id))
    db.session.commit()
    return ok({"favorite": True}, message="已加入收藏")


@favorites_bp.get("", strict_slashes=False)
@require_login
def list_favorites():
    """我的收藏，按收藏时间倒序返回商品卡片。"""
    rows = (
        Favorite.query.filter(Favorite.user_id == g.current_user.id)
        .order_by(Favorite.created_at.desc(), Favorite.id.desc())
        .all()
    )
    item_ids = [row.item_id for row in rows]
    if not item_ids:
        return ok([])

    items = Item.query.filter(
        Item.id.in_(item_ids), Item.is_deleted == False
    ).all()
    by_id = {item.id: item for item in items}
    return ok([by_id[item_id].to_card_dict() for item_id in item_ids if item_id in by_id])


@favorites_bp.get("/check")
@require_login
def check_favorite():
    """详情页判断是否已收藏。"""
    item_id = request.args.get("itemId", type=int)
    if not item_id:
        return ok(False)

    exists = Favorite.query.filter_by(
        user_id=g.current_user.id, item_id=item_id
    ).first()
    return ok(exists is not None)
