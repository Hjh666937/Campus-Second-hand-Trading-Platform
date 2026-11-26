from datetime import datetime

from sqlalchemy import Identity, Integer, Numeric, Unicode

from extensions import db


class Order(db.Model):
    """订单表，对应 dbo.orders。"""

    __tablename__ = "orders"

    id = db.Column(Integer, Identity(1, 1), primary_key=True)
    order_no = db.Column(Unicode(32), unique=True, nullable=False)
    item_id = db.Column(Integer, db.ForeignKey("items.id"), nullable=False)
    buyer_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False)
    seller_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False)
    price = db.Column(Numeric(10, 2), nullable=False)
    status = db.Column(Unicode(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    finished_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)

    item = db.relationship("Item", lazy="joined")
    buyer = db.relationship("User", foreign_keys=[buyer_id], lazy="joined")
    seller = db.relationship("User", foreign_keys=[seller_id], lazy="joined")
    review = db.relationship(
        "Review", uselist=False, lazy="joined", back_populates="order"
    )

    def to_dict(self):
        """订单字段与前端 Mock 结构保持一致。"""
        return {
            "id": self.id,
            "orderNo": self.order_no,
            "itemId": self.item_id,
            "itemTitle": self.item.title if self.item else "",
            "itemCover": self.item.cover if self.item else None,
            "price": float(self.price),
            "buyerAccount": self.buyer.account if self.buyer else "",
            "buyerNickname": self.buyer.nickname if self.buyer else "",
            "sellerNickname": self.seller.nickname if self.seller else "",
            "status": self.status,
            "reviewed": self.review is not None,
            "createdAt": _format_time(self.created_at),
            "finishedAt": _format_time(self.finished_at),
        }


class Review(db.Model):
    """交易评价表，对应 dbo.reviews，一单一评。"""

    __tablename__ = "reviews"

    id = db.Column(Integer, Identity(1, 1), primary_key=True)
    order_id = db.Column(
        Integer, db.ForeignKey("orders.id"), unique=True, nullable=False
    )
    item_id = db.Column(Integer, db.ForeignKey("items.id"), nullable=False)
    reviewer_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False)
    target_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.SmallInteger, nullable=False)
    content = db.Column(Unicode(500))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    order = db.relationship("Order", lazy="select", back_populates="review")
    item = db.relationship("Item", lazy="joined")
    reviewer = db.relationship("User", foreign_keys=[reviewer_id], lazy="joined")
    target = db.relationship("User", foreign_keys=[target_id], lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "orderId": self.order_id,
            "itemId": self.item_id,
            "itemTitle": self.item.title if self.item else "",
            "sellerNickname": self.target.nickname if self.target else "",
            "buyerAccount": self.reviewer.account if self.reviewer else "",
            "buyerNickname": self.reviewer.nickname if self.reviewer else "",
            "rating": int(self.rating),
            "content": self.content or "",
            "createdAt": _format_time(self.created_at),
        }


def _format_time(value):
    return value.strftime("%Y-%m-%d %H:%M") if value else None
