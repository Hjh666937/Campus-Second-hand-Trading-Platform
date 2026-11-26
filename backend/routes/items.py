import base64
import os
import uuid
from datetime import datetime, timedelta

from flask import Blueprint, current_app, g, request
from sqlalchemy import or_

from extensions import db
from models import Item, ItemImage, Order, User
from utils.auth import optional_login, require_login
from utils.response import fail, ok

items_bp = Blueprint("items", __name__, url_prefix="/api/items")

CONDITIONS = {"全新", "九成新", "八成新", "七成新", "六成新及以下"}
STATUSES = {"on_sale", "locked", "sold", "off_shelf"}
SORTS = {
    "latest": (Item.created_at.desc(),),
    "priceAsc": (Item.price.asc(),),
    "priceDesc": (Item.price.desc(),),
    "hot": (Item.view_count.desc(),),
}
IMAGE_MIME_EXT = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}
MAX_IMAGES = 4


def _clean(value):
    return value.strip() if isinstance(value, str) else ""


def _save_image(raw, host_url):
    """把 base64 data URL 落盘，返回可访问的绝对 URL；http 链接原样保留。"""
    if not isinstance(raw, str) or not raw:
        return None
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    if not raw.startswith("data:image/"):
        return None

    header, _, encoded = raw.partition(",")
    mime = header[len("data:"):].split(";")[0]
    ext = IMAGE_MIME_EXT.get(mime)
    if not ext:
        return None

    try:
        content = base64.b64decode(encoded)
    except (ValueError, TypeError):
        return None

    folder = os.path.join(current_app.config["UPLOAD_DIR"], "items")
    os.makedirs(folder, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    with open(os.path.join(folder, filename), "wb") as fp:
        fp.write(content)
    return f"{host_url.rstrip('/')}/uploads/items/{filename}"


def _int_param(name, default, minimum=None):
    try:
        value = int(request.args.get(name, default))
    except (TypeError, ValueError):
        return default
    if minimum is not None and value < minimum:
        return default
    return value


def _float_param(name):
    raw = request.args.get(name)
    if raw in (None, ""):
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


@items_bp.get("/", strict_slashes=False)
def list_items():
    """商品列表：关键词、分类、价格区间、校区、卖家、状态、排序、分页。"""
    page = _int_param("page", 1, minimum=1)
    size = min(_int_param("size", 12, minimum=1), 100)
    keyword = _clean(request.args.get("keyword", ""))
    campus = _clean(request.args.get("campus", ""))
    seller_nickname = _clean(request.args.get("sellerNickname", ""))
    status = _clean(request.args.get("status", "on_sale")) or "on_sale"
    sort = request.args.get("sort", "latest")
    category_id = _int_param("categoryId", 0)
    seller_id = _int_param("sellerId", 0)
    min_price = _float_param("minPrice")
    max_price = _float_param("maxPrice")

    query = Item.query.filter(Item.is_deleted == False)

    if status != "all":
        query = query.filter(Item.status == status)
    if category_id:
        query = query.filter(Item.category_id == category_id)
    if campus:
        query = query.filter(Item.campus == campus)
    if min_price is not None:
        query = query.filter(Item.price >= min_price)
    if max_price is not None:
        query = query.filter(Item.price <= max_price)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(or_(
            Item.title.like(like),
            Item.description.like(like),
            Item.campus.like(like),
            Item.condition.like(like),
        ))
    if seller_id:
        query = query.filter(Item.seller_id == seller_id)
    elif seller_nickname:
        seller_ids = [
            row.id for row in User.query.filter_by(nickname=seller_nickname).all()
        ]
        if not seller_ids:
            return ok({"list": [], "total": 0, "page": page, "size": size})
        query = query.filter(Item.seller_id.in_(seller_ids))

    total = query.count()
    rows = (
        query.order_by(*SORTS.get(sort, SORTS["latest"]))
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return ok({
        "list": [item.to_card_dict() for item in rows],
        "total": total,
        "page": page,
        "size": size,
    })


@items_bp.get("/<int:item_id>")
def item_detail(item_id):
    optional_login()
    item = Item.query.filter(Item.id == item_id, Item.is_deleted == False).first()
    if not item:
        return fail("商品不存在或已删除", 404)

    # 下架 / 已售商品只有管理员和商品卖家能看（卖家管理自己的商品、处理订单需要）
    if item.status != "on_sale":
        viewer = getattr(g, "current_user", None)
        viewer_id = getattr(viewer, "id", None)
        viewer_role = getattr(viewer, "role", None)
        if viewer_role != "admin" and viewer_id != item.seller_id:
            return fail("商品已下架", 404)

    data = item.to_detail_dict()
    # 卖家在详情页据此提醒「有待确认订单」
    data["activeOrderCount"] = Order.query.filter(
        Order.item_id == item.id,
        Order.status.in_(["pending", "confirmed"]),
    ).count()
    return ok(data)


@items_bp.post("/<int:item_id>/view")
def record_view(item_id):
    item = Item.query.filter(
        Item.id == item_id, Item.is_deleted == False, Item.status == "on_sale"
    ).first()
    if not item:
        return fail("商品不存在或已下架", 404)
    item.view_count = item.view_count + 1
    db.session.commit()
    return ok({"viewCount": item.view_count})


def _validate_item_payload(payload):
    """校验并返回整理后的字段，出错则抛 ValueError(消息)。"""
    data = {}

    if "title" in payload:
        title = _clean(payload.get("title"))
        if not (4 <= len(title) <= 40):
            raise ValueError("标题需 4-40 个字")
        data["title"] = title

    if "categoryId" in payload:
        try:
            category_id = int(payload.get("categoryId"))
        except (TypeError, ValueError):
            raise ValueError("请选择商品分类")
        data["category_id"] = category_id

    if "price" in payload:
        try:
            price = float(payload.get("price"))
        except (TypeError, ValueError):
            raise ValueError("请输入正确的价格")
        if not (0 < price <= 99999):
            raise ValueError("价格需在 0-99999 之间")
        data["price"] = price

    if "condition" in payload:
        condition = _clean(payload.get("condition"))
        if condition not in CONDITIONS:
            raise ValueError("请选择商品成色")
        data["condition"] = condition

    if "campus" in payload:
        campus = _clean(payload.get("campus"))
        if not (2 <= len(campus) <= 20):
            raise ValueError("校区需 2-20 个字")
        data["campus"] = campus

    if "description" in payload:
        description = _clean(payload.get("description"))
        if not (5 <= len(description) <= 200):
            raise ValueError("描述需 5-200 个字")
        data["description"] = description

    return data


@items_bp.post("/", strict_slashes=False)
@require_login
def create_item():
    if g.current_user.role == "admin":
        return fail("管理员账号不能发布商品", 403)

    payload = request.get_json(silent=True) or {}

    try:
        data = _validate_item_payload(payload)
    except ValueError as error:
        return fail(str(error), 422)

    required = {"title", "category_id", "price", "condition", "campus", "description"}
    if not required.issubset(data):
        return fail("请完整填写商品信息", 422)

    # 同一卖家 60 秒内只允许发布一件，避免连续刷屏
    recent = Item.query.filter(
        Item.seller_id == g.current_user.id,
        Item.created_at >= datetime.now() - timedelta(seconds=60),
    ).first()
    if recent:
        return fail("发布太频繁，请 60 秒后再试", 429)

    raw_images = payload.get("images") or []
    if not isinstance(raw_images, list) or not (1 <= len(raw_images) <= MAX_IMAGES):
        return fail(f"请上传 1-{MAX_IMAGES} 张商品图片", 422)

    host_url = request.host_url
    urls = [url for url in (_save_image(raw, host_url) for raw in raw_images) if url]
    if not urls:
        return fail("图片格式不支持，请上传 JPG / PNG / WebP", 422)

    item = Item(
        seller_id=g.current_user.id,
        category_id=data["category_id"],
        title=data["title"],
        description=data["description"],
        price=data["price"],
        condition=data["condition"],
        campus=data["campus"],
        cover=urls[0],
        status="on_sale",
    )
    db.session.add(item)
    db.session.flush()

    for index, url in enumerate(urls):
        db.session.add(ItemImage(item_id=item.id, url=url, sort=index))

    db.session.commit()
    return ok(item.to_detail_dict(), message="发布成功", status=201)


@items_bp.put("/<int:item_id>")
@require_login
def update_item(item_id):
    item = Item.query.filter(Item.id == item_id, Item.is_deleted == False).first()
    if not item:
        return fail("商品不存在或已删除", 404)
    if item.seller_id != g.current_user.id and g.current_user.role != "admin":
        return fail("只能修改自己发布的商品", 403)

    payload = request.get_json(silent=True) or {}
    try:
        data = _validate_item_payload(payload)
    except ValueError as error:
        return fail(str(error), 422)

    for field, value in data.items():
        setattr(item, field, value)

    raw_images = payload.get("images")
    if isinstance(raw_images, list) and raw_images:
        if len(raw_images) > MAX_IMAGES:
            return fail(f"最多上传 {MAX_IMAGES} 张图片", 422)
        urls = [url for url in (_save_image(raw, request.host_url) for raw in raw_images) if url]
        if urls:
            for old in list(item.images_rel):
                db.session.delete(old)
            db.session.flush()
            for index, url in enumerate(urls):
                db.session.add(ItemImage(item_id=item.id, url=url, sort=index))
            item.cover = urls[0]

    db.session.commit()
    return ok(item.to_detail_dict(), message="修改已保存")


@items_bp.patch("/<int:item_id>/status")
@require_login
def update_item_status(item_id):
    item = Item.query.filter(Item.id == item_id, Item.is_deleted == False).first()
    if not item:
        return fail("商品不存在或已删除", 404)
    if item.seller_id != g.current_user.id and g.current_user.role != "admin":
        return fail("无权修改该商品状态", 403)

    status = _clean((request.get_json(silent=True) or {}).get("status"))
    if status not in STATUSES:
        return fail("商品状态不合法", 422)

    item.status = status
    cancelled_orders = 0
    if status == "sold":
        # 标记已售后，该商品还没确认的订单自动取消
        pending_orders = Order.query.filter(
            Order.item_id == item.id, Order.status == "pending"
        ).all()
        for row in pending_orders:
            row.status = "cancelled"
            row.cancelled_at = datetime.now()
        cancelled_orders = len(pending_orders)

    db.session.commit()
    data = item.to_card_dict()
    data["cancelledOrders"] = cancelled_orders
    message = "状态已更新"
    if status == "sold" and cancelled_orders:
        message = f"已标记已售，{cancelled_orders} 笔待确认订单已自动取消"
    return ok(data, message=message)


@items_bp.delete("/<int:item_id>")
@require_login
def delete_item(item_id):
    item = Item.query.filter(Item.id == item_id, Item.is_deleted == False).first()
    if not item:
        return fail("商品不存在或已删除", 404)
    if item.seller_id != g.current_user.id:
        return fail("只能删除自己发布的商品", 403)

    item.is_deleted = True
    item.status = "off_shelf"
    db.session.commit()
    return ok(message="商品已删除")
