from datetime import datetime

from sqlalchemy import Identity, Integer, Unicode

from extensions import db


class Category(db.Model):
    """商品分类表，对应 dbo.categories。"""

    __tablename__ = "categories"

    id = db.Column(Integer, Identity(1, 1), primary_key=True)
    name = db.Column(Unicode(30), nullable=False, unique=True)
    sort = db.Column(Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "sort": self.sort}
