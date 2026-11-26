from datetime import datetime

from sqlalchemy import Identity, Integer

from extensions import db


class Favorite(db.Model):
    """收藏表，对应 dbo.favorites。"""

    __tablename__ = "favorites"

    id = db.Column(Integer, Identity(1, 1), primary_key=True)
    user_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False)
    item_id = db.Column(Integer, db.ForeignKey("items.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
