from datetime import datetime

from flask import Blueprint, g, request
from sqlalchemy import or_

from extensions import db
from models import Conversation, Item, Message
from utils.auth import require_login
from utils.response import fail, ok

chat_bp = Blueprint("chat", __name__, url_prefix="/api/conversations")


def _clean(value):
    return value.strip() if isinstance(value, str) else ""


def _get_conversation(conversation_id):
    """取会话并校验当前用户是会话参与者，失败返回 (会话, 错误响应)。"""
    conversation = db.session.get(Conversation, conversation_id)
    if not conversation:
        return None, fail("会话不存在", 404)

    user_id = g.current_user.id
    if user_id not in (conversation.buyer_id, conversation.seller_id):
        return None, fail("无权查看该会话", 403)
    return conversation, None


@chat_bp.post("", strict_slashes=False)
@require_login
def open_conversation():
    """买家点「联系卖家」：同一商品只保留一条会话。"""
    if g.current_user.role == "admin":
        return fail("管理员不能发起聊天", 403)

    payload = request.get_json(silent=True) or {}
    try:
        item_id = int(payload.get("itemId"))
    except (TypeError, ValueError):
        return fail("请选择商品", 422)

    item = Item.query.filter(Item.id == item_id, Item.is_deleted == False).first()
    if not item:
        return fail("商品不存在或已删除", 404)
    if item.seller_id == g.current_user.id:
        return fail("不能和自己聊天", 400)

    conversation = Conversation.query.filter_by(
        item_id=item.id, buyer_id=g.current_user.id
    ).first()
    if not conversation:
        conversation = Conversation(
            item_id=item.id,
            buyer_id=g.current_user.id,
            seller_id=item.seller_id,
            last_at=datetime.now(),
        )
        db.session.add(conversation)
        db.session.commit()

    return ok(conversation.to_dict(g.current_user.id))


@chat_bp.get("", strict_slashes=False)
@require_login
def list_conversations():
    """我的会话，按最近消息时间倒序。"""
    user_id = g.current_user.id
    rows = (
        Conversation.query.filter(
            or_(Conversation.buyer_id == user_id, Conversation.seller_id == user_id)
        )
        .order_by(Conversation.last_at.desc(), Conversation.id.desc())
        .all()
    )
    return ok([row.to_dict(user_id) for row in rows])


@chat_bp.get("/unread-count")
@require_login
def unread_count():
    """未读消息总数，顶部导航红点用。"""
    user_id = g.current_user.id
    rows = Conversation.query.filter(
        or_(Conversation.buyer_id == user_id, Conversation.seller_id == user_id)
    ).all()
    total = sum(
        row.buyer_unread if row.buyer_id == user_id else row.seller_unread
        for row in rows
    )
    return ok(total)


@chat_bp.get("/<int:conversation_id>/messages")
@require_login
def list_messages(conversation_id):
    conversation, error = _get_conversation(conversation_id)
    if error:
        return error

    rows = (
        Message.query.filter(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc(), Message.id.asc())
        .all()
    )
    return ok([row.to_dict() for row in rows])


@chat_bp.post("/<int:conversation_id>/messages")
@require_login
def send_message(conversation_id):
    conversation, error = _get_conversation(conversation_id)
    if error:
        return error

    payload = request.get_json(silent=True) or {}
    content = _clean(payload.get("content"))
    if not content:
        return fail("消息不能为空", 422)
    if len(content) > 1000:
        return fail("消息最多 1000 个字", 422)

    now = datetime.now()
    message = Message(
        conversation_id=conversation.id,
        sender_id=g.current_user.id,
        type="text",
        content=content,
        created_at=now,
    )
    db.session.add(message)

    conversation.last_message = content[:200]
    conversation.last_at = now
    if conversation.buyer_id == g.current_user.id:
        conversation.seller_unread = (conversation.seller_unread or 0) + 1
    else:
        conversation.buyer_unread = (conversation.buyer_unread or 0) + 1

    db.session.commit()
    return ok(message.to_dict(), message="已发送", status=201)


@chat_bp.post("/<int:conversation_id>/read")
@require_login
def mark_read(conversation_id):
    conversation, error = _get_conversation(conversation_id)
    if error:
        return error

    user_id = g.current_user.id
    if conversation.buyer_id == user_id:
        conversation.buyer_unread = 0
    else:
        conversation.seller_unread = 0

    Message.query.filter(
        Message.conversation_id == conversation.id,
        Message.sender_id != user_id,
        Message.is_read == False,
    ).update({Message.is_read: True}, synchronize_session=False)

    db.session.commit()
    return ok(True, message="已读")
