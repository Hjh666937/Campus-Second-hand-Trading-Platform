import random
from datetime import datetime

from flask import Blueprint, g, request

from extensions import db
from models import Item, Order, Review, User
from utils.auth import require_login
from utils.notify import notify
from utils.response import fail, ok

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")
reviews_bp = Blueprint("reviews", __name__, url_prefix="/api/reviews")

# 合法状态流转：待确认 → 待交易 → 已完成，中途可取消
TRANSITIONS = {
    "pending": {"confirmed", "cancelled"},
    "confirmed": {"completed", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}


def _order_no():
    return f"C{datetime.now():%Y%m%d%H%M%S}{random.randint(1000, 9999)}"


@orders_bp.post("/", strict_slashes=False)
@require_login
def create_order():
    """下单：同一买家对同一商品只允许一笔进行中的订单。"""
    if g.current_user.role == "admin":
        return fail("管理员账号不能下单", 403)

    payload = request.get_json(silent=True) or {}
    try:
        item_id = int(payload.get("itemId"))
    except (TypeError, ValueError):
        return fail("请选择要购买的商品", 422)

    item = Item.query.filter(Item.id == item_id, Item.is_deleted == False).first()
    if not item:
        return fail("商品不存在或已删除", 404)
    if item.seller_id == g.current_user.id:
        return fail("不能购买自己发布的商品", 400)
    if item.status != "on_sale":
        return fail("商品已下架或已售出", 400)

    duplicated = Order.query.filter(
        Order.item_id == item.id,
        Order.buyer_id == g.current_user.id,
        Order.status.in_(["pending", "confirmed"]),
    ).first()
    if duplicated:
        return fail("你已经下过单了，去「我的」里查看", 409)

    order = Order(
        order_no=_order_no(),
        item_id=item.id,
        buyer_id=g.current_user.id,
        seller_id=item.seller_id,
        price=item.price,
        status="pending",
    )
    db.session.add(order)
    db.session.flush()
    notify(
        item.seller_id,
        "order_created",
        "收到新订单",
        f"{g.current_user.nickname} 想购买「{item.title}」，请及时确认",
        order.id,
    )
    db.session.commit()
    return ok(order.to_dict(), message="下单成功", status=201)


@orders_bp.get("/", strict_slashes=False)
@require_login
def list_orders():
    """我的订单：role=buyer 买到的（不含已取消），role=seller 卖出的。"""
    role = request.args.get("role", "buyer")
    query = Order.query

    if role == "seller":
        query = query.filter(Order.seller_id == g.current_user.id)
    else:
        query = query.filter(
            Order.buyer_id == g.current_user.id,
            Order.status != "cancelled",
        )

    rows = query.order_by(Order.created_at.desc(), Order.id.desc()).all()
    return ok([row.to_dict() for row in rows])


@orders_bp.patch("/<int:order_id>/status")
@require_login
def update_order_status(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return fail("订单不存在", 404)

    status = (request.get_json(silent=True) or {}).get("status")
    if status not in {"confirmed", "completed", "cancelled"}:
        return fail("订单状态不合法", 422)

    is_buyer = order.buyer_id == g.current_user.id
    is_seller = order.seller_id == g.current_user.id
    if not (is_buyer or is_seller):
        return fail("无权操作该订单", 403)
    # 动作与角色对应：卖家负责确认成交 / 拒绝，买家负责取消 / 确认收货
    if status == "confirmed" and not is_seller:
        return fail("只有卖家可以确认订单", 403)
    if status == "completed" and not is_buyer:
        return fail("只有买家可以确认收货", 403)
    # 卖家只能处理待确认订单：确认成交或拒绝
    if is_seller and not is_buyer:
        if order.status != "pending" or status not in {"confirmed", "cancelled"}:
            return fail("卖家只能确认或拒绝待确认订单", 403)
    if status not in TRANSITIONS.get(order.status, set()):
        return fail("当前订单状态不支持该操作", 400)

    order.status = status
    item_title = order.item.title if order.item else ""
    cancelled_others = 0
    if status == "completed":
        order.finished_at = datetime.now()
        # 交易完成，商品标记为已售，避免继续挂在首页
        if order.item and not order.item.is_deleted:
            order.item.status = "sold"
        notify(
            order.seller_id,
            "order_completed",
            "交易已完成",
            f"买家已确认收货：「{item_title}」",
            order.id,
        )
    elif status == "cancelled":
        order.cancelled_at = datetime.now()
        if is_buyer:
            notify(
                order.seller_id,
                "order_cancelled",
                "买家取消了订单",
                f"「{item_title}」的订单已取消",
                order.id,
            )
        else:
            notify(
                order.buyer_id,
                "order_cancelled",
                "卖家拒绝了订单",
                f"「{item_title}」的订单已被卖家拒绝",
                order.id,
            )
    elif status == "confirmed":
        notify(
            order.buyer_id,
            "order_confirmed",
            "卖家已确认订单",
            f"「{item_title}」已确认，请按约定当面交易",
            order.id,
        )
        # 商品已确认成交，同一商品其它待确认订单自动取消，避免重复卖出
        others = Order.query.filter(
            Order.item_id == order.item_id,
            Order.id != order.id,
            Order.status == "pending",
        ).all()
        for row in others:
            row.status = "cancelled"
            row.cancelled_at = datetime.now()
            notify(
                row.buyer_id,
                "order_cancelled",
                "订单已自动取消",
                f"「{item_title}」已确认给其他买家，你的订单已自动取消",
                row.id,
            )
        cancelled_others = len(others)

    db.session.commit()

    if status == "confirmed":
        message = "订单已确认，请与买家当面交易"
        if cancelled_others:
            message = f"订单已确认，同商品其他 {cancelled_others} 笔待确认订单已自动取消"
    elif status == "cancelled":
        message = "订单已取消"
    elif status == "completed":
        message = "交易已完成"
    else:
        message = "状态已更新"
    return ok(order.to_dict(), message=message)


# 星级 → 信用分目标值，用于折算卖家信誉分
RATING_CREDIT = {5: 100, 4: 95, 3: 75, 2: 50, 1: 30}
# 每次评价调整信用分的比例：新信用分 = 原信用分 × 0.8 + 星级目标分 × 0.2
CREDIT_RATIO = 0.2


def _apply_credit(seller, rating):
    """按星级比例调整卖家信用分，保持在 0-100 之间。"""
    target = RATING_CREDIT.get(rating, 60)
    credit = seller.credit * (1 - CREDIT_RATIO) + target * CREDIT_RATIO
    seller.credit = max(0, min(100, round(credit)))


@orders_bp.post("/<int:order_id>/review")
@require_login
def review_order(order_id):
    """买家评价已完成订单（星级 + 可选文字），一单一评，星级折算进卖家信用分。"""
    order = db.session.get(Order, order_id)
    if not order:
        return fail("订单不存在", 404)
    if order.buyer_id != g.current_user.id:
        return fail("只能评价自己买到的订单", 403)
    if order.status != "completed":
        return fail("订单完成后才能评价", 400)
    if order.review:
        return fail("这笔订单已经评价过了", 409)

    payload = request.get_json(silent=True) or {}
    try:
        rating = int(payload.get("rating"))
    except (TypeError, ValueError):
        return fail("请选择 1-5 星评分", 422)
    if not 1 <= rating <= 5:
        return fail("请选择 1-5 星评分", 422)

    content = (payload.get("content") or "").strip()
    if len(content) > 500:
        return fail("评价最多 500 个字", 422)

    review = Review(
        order_id=order.id,
        item_id=order.item_id,
        reviewer_id=g.current_user.id,
        target_id=order.seller_id,
        rating=rating,
        content=content or None,
    )
    db.session.add(review)

    if order.seller:
        _apply_credit(order.seller, rating)

    notify(
        order.seller_id,
        "order_reviewed",
        f"收到 {rating} 星评价",
        f"{g.current_user.nickname} 评价了「{order.item.title if order.item else ''}」",
        order.id,
    )

    db.session.commit()
    message = "评价已提交"
    if order.seller:
        message = f"评价已提交，卖家信用分更新为 {order.seller.credit} 分"
    return ok(review.to_dict(), message=message, status=201)


@reviews_bp.get("/", strict_slashes=False)
def list_reviews():
    """某个卖家收到的评价，?seller=昵称。"""
    nickname = (request.args.get("seller") or "").strip()
    if not nickname:
        return ok([])

    user_ids = [row.id for row in User.query.filter_by(nickname=nickname).all()]
    if not user_ids:
        return ok([])

    rows = (
        Review.query.filter(Review.target_id.in_(user_ids))
        .order_by(Review.created_at.desc(), Review.id.desc())
        .all()
    )
    return ok([row.to_dict() for row in rows])
