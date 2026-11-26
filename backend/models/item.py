from datetime import datetime

from sqlalchemy import Identity, Integer, Numeric, Unicode

from extensions import db


class Item(db.Model):
    """商品表，对应 dbo.items。"""

    __tablename__ = "items"

    id = db.Column(Integer, Identity(1, 1), primary_key=True)
    seller_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(Integer, db.ForeignKey("categories.id"), nullable=False)
    title = db.Column(Unicode(80), nullable=False)
    description = db.Column(Unicode)
    price = db.Column(Numeric(10, 2), nullable=False)
    condition = db.Column(Unicode(20), nullable=False)
    campus = db.Column(Unicode(50), nullable=False)
    cover = db.Column(Unicode(500))
    status = db.Column(Unicode(20), nullable=False, default="on_sale")
    view_count = db.Column(Integer, nullable=False, default=0)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now,
                           onupdate=datetime.now)

    seller = db.relationship("User", lazy="joined")
    images_rel = db.relationship(
        "ItemImage",
        lazy="select",
        cascade="all, delete-orphan",
        order_by="ItemImage.sort",
    )

    def to_card_dict(self):
        """列表卡片需要的字段，与前端 Mock 结构一致。"""
        return {
            "id": self.id,
            "title": self.title,
            "price": float(self.price),
            "cover": self.cover,
            "condition": self.condition,
            "campus": self.campus,
            "categoryId": self.category_id,
            "sellerNickname": self.seller.nickname if self.seller else "",
            "viewCount": self.view_count,
            "createdAt": self.created_at.strftime("%Y-%m-%d"),
            "status": self.status,
        }

    def to_detail_dict(self):
        data = self.to_card_dict()
        images = [img.url for img in self.images_rel]
        data.update({
            "description": self.description or "",
            "images": images or ([self.cover] if self.cover else []),
            "sellerId": self.seller_id,
            "seller": {
                "nickname": self.seller.nickname if self.seller else "",
                "avatar": self.seller.avatar if self.seller else None,
                "campus": self.seller.campus if self.seller else "",
                "credit": self.seller.credit if self.seller else None,
            },
        })
        return data


class ItemImage(db.Model):
    """商品图片表，对应 dbo.item_images。"""

    __tablename__ = "item_images"

    id = db.Column(Integer, Identity(1, 1), primary_key=True)
    item_id = db.Column(Integer, db.ForeignKey("items.id"), nullable=False)
    url = db.Column(Unicode(500), nullable=False)
    sort = db.Column(Integer, nullable=False, default=0)
