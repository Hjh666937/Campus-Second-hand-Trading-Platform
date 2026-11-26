from datetime import datetime

from sqlalchemy import Identity, Integer, Unicode

from extensions import db


class Conversation(db.Model):
    """会话表，对应 dbo.conversations。"""

    __tablename__ = "conversations"

    id = db.Column(Integer, Identity(1, 1), primary_key=True)
    item_id = db.Column(Integer, db.ForeignKey("items.id"), nullable=False)
    buyer_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False)
    seller_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False)
    last_message = db.Column(Unicode(200))
    last_at = db.Column(db.DateTime)
    buyer_unread = db.Column(Integer, nullable=False, default=0)
    seller_unread = db.Column(Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    item = db.relationship("Item", lazy="joined")
    buyer = db.relationship("User", foreign_keys=[buyer_id], lazy="joined")
    seller = db.relationship("User", foreign_keys=[seller_id], lazy="joined")

    def to_dict(self, viewer_id):
        """会话字段对齐前端 Mock，unread/peerNickname 按当前查看者计算。"""
        is_buyer = viewer_id == self.buyer_id
        peer = self.seller if is_buyer else self.buyer
        return {
            "id": self.id,
            "itemId": self.item_id,
            "itemTitle": self.item.title if self.item else "",
            "itemCover": self.item.cover if self.item else None,
            "sellerNickname": self.seller.nickname if self.seller else "",
            "buyerNickname": self.buyer.nickname if self.buyer else "",
            "peerNickname": peer.nickname if peer else "",
            "lastMessage": self.last_message or "",
            "lastAt": self.last_at.isoformat() if self.last_at else None,
            "buyerUnread": self.buyer_unread,
            "sellerUnread": self.seller_unread,
            "unread": self.buyer_unread if is_buyer else self.seller_unread,
        }


class Message(db.Model):
    """消息表，对应 dbo.messages。"""

    __tablename__ = "messages"

    id = db.Column(Integer, Identity(1, 1), primary_key=True)
    conversation_id = db.Column(
        Integer, db.ForeignKey("conversations.id"), nullable=False
    )
    sender_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False)
    type = db.Column(Unicode(10), nullable=False, default="text")
    content = db.Column(Unicode, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    sender = db.relationship("User", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "conversationId": self.conversation_id,
            "senderAccount": self.sender.account if self.sender else "",
            "senderNickname": self.sender.nickname if self.sender else "",
            "type": self.type,
            "content": self.content,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
