from flask import Blueprint, g

from extensions import db
from models import Notification
from utils.auth import require_login
from utils.response import ok

notifications_bp = Blueprint(
    "notifications", __name__, url_prefix="/api/notifications"
)


@notifications_bp.get("", strict_slashes=False)
@require_login
def list_notifications():
    """当前用户最近 50 条站内通知 + 未读数。"""
    rows = (
        Notification.query.filter(Notification.user_id == g.current_user.id)
        .order_by(Notification.created_at.desc(), Notification.id.desc())
        .limit(50)
        .all()
    )
    unread = Notification.query.filter(
        Notification.user_id == g.current_user.id,
        Notification.is_read == False,
    ).count()
    return ok({"list": [row.to_dict() for row in rows], "unread": unread})


@notifications_bp.post("/read")
@require_login
def mark_all_read():
    Notification.query.filter(
        Notification.user_id == g.current_user.id,
        Notification.is_read == False,
    ).update({Notification.is_read: True}, synchronize_session=False)
    db.session.commit()
    return ok({"unread": 0}, message="已全部标记为已读")
