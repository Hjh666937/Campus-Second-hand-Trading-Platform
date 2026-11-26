from flask import Blueprint, g, request

from extensions import db
from models import Item, Report
from utils.auth import require_login
from utils.response import fail, ok

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

REASONS = {"虚假信息", "违禁物品", "价格欺诈", "盗图/侵权", "其他"}


def _clean(value):
    return value.strip() if isinstance(value, str) else ""


@reports_bp.post("", strict_slashes=False)
@require_login
def create_report():
    """买家举报商品，进入管理员待处理队列。"""
    payload = request.get_json(silent=True) or {}
    try:
        item_id = int(payload.get("itemId"))
    except (TypeError, ValueError):
        return fail("请选择要举报的商品", 422)

    reason = _clean(payload.get("reason"))
    if reason not in REASONS:
        return fail("请选择举报原因", 422)

    detail = _clean(payload.get("detail"))
    if len(detail) > 500:
        return fail("补充说明最多 500 个字", 422)

    item = Item.query.filter(Item.id == item_id, Item.is_deleted == False).first()
    if not item:
        return fail("商品不存在或已删除", 404)
    if item.seller_id == g.current_user.id:
        return fail("不能举报自己发布的商品", 400)

    db.session.add(Report(
        item_id=item.id,
        reporter_id=g.current_user.id,
        reason=reason,
        detail=detail or None,
        status="pending",
    ))
    db.session.commit()
    return ok(True, message="举报已提交，管理员会尽快处理", status=201)
