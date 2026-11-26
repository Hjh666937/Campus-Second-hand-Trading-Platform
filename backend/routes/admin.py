from datetime import datetime

from flask import Blueprint, g, request
from sqlalchemy import func
from werkzeug.security import generate_password_hash

from extensions import db
from models import Item, Order, Report, User
from utils.auth import require_admin
from utils.response import fail, ok

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

USER_STATUSES = {"active", "banned"}
REPORT_STATUSES = {"handled", "rejected"}


@admin_bp.get("/stats")
@require_admin
def stats():
    """平台数据概况，全部来自数据库。"""
    turnover = (
        db.session.query(func.coalesce(func.sum(Order.price), 0))
        .filter(Order.status == "completed")
        .scalar()
    )
    return ok({
        "userCount": User.query.count(),
        "bannedCount": User.query.filter(User.status == "banned").count(),
        "publishedCount": Item.query.filter(Item.is_deleted == False).count(),
        "orderCount": Order.query.count(),
        "completedCount": Order.query.filter(Order.status == "completed").count(),
        "turnover": float(turnover or 0),
        "pendingReports": Report.query.filter(Report.status == "pending").count(),
    })


@admin_bp.get("/users")
@require_admin
def list_users():
    rows = User.query.order_by(User.id.asc()).all()
    return ok([
        {
            "account": row.account,
            "nickname": row.nickname,
            "campus": row.campus or "",
            "role": row.role,
            "status": row.status,
            "bannedAt": None,
        }
        for row in rows
    ])


@admin_bp.patch("/users/<account>/status")
@require_admin
def update_user_status(account):
    """封禁 / 解封普通用户，管理员账号不允许操作。"""
    user = User.query.filter_by(account=account).first()
    if not user:
        return fail("用户不存在", 404)
    if user.role == "admin":
        return fail("管理员账号不能封禁", 403)

    status = (request.get_json(silent=True) or {}).get("status")
    if status not in USER_STATUSES:
        return fail("用户状态不合法", 422)

    user.status = status
    db.session.commit()
    return ok(True, message="已封禁" if status == "banned" else "已解封")


@admin_bp.patch("/users/<account>/password/reset")
@require_admin
def reset_password(account):
    """重置为初始密码：账号后 6 位（不足 6 位用 123456）。"""
    user = User.query.filter_by(account=account).first()
    if not user:
        return fail("用户不存在", 404)
    if user.role == "admin":
        return fail("不能重置管理员密码", 403)

    new_password = account[-6:] if len(account) >= 6 else "123456"
    user.password_hash = generate_password_hash(new_password)
    user.must_change_password = True
    db.session.commit()
    return ok(True, message=f"已重置为初始密码：{new_password}")


@admin_bp.get("/reports")
@require_admin
def list_reports():
    rows = Report.query.order_by(Report.created_at.desc(), Report.id.desc()).all()
    return ok([
        {
            "id": row.id,
            "itemId": row.item_id,
            "itemTitle": row.item.title if row.item else "",
            "reason": row.reason,
            "detail": row.detail or "",
            "account": row.reporter.account if row.reporter else "",
            "nickname": row.reporter.nickname if row.reporter else "",
            "status": row.status,
            "createdAt": row.created_at.strftime("%Y-%m-%d %H:%M") if row.created_at else "",
        }
        for row in rows
    ])


@admin_bp.patch("/reports/<int:report_id>")
@require_admin
def handle_report(report_id):
    report = db.session.get(Report, report_id)
    if not report:
        return fail("举报不存在", 404)

    status = (request.get_json(silent=True) or {}).get("status")
    if status not in REPORT_STATUSES:
        return fail("处理状态不合法", 422)

    report.status = status
    report.handled_by = g.current_user.id
    report.handled_at = datetime.now()
    db.session.commit()
    return ok(True, message="已处理")
