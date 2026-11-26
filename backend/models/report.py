from datetime import datetime

from sqlalchemy import Identity, Integer, Unicode

from extensions import db


class Report(db.Model):
    """举报表，对应 dbo.reports。"""

    __tablename__ = "reports"

    id = db.Column(Integer, Identity(1, 1), primary_key=True)
    item_id = db.Column(Integer, db.ForeignKey("items.id"), nullable=False)
    reporter_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False)
    reason = db.Column(Unicode(50), nullable=False)
    detail = db.Column(Unicode(500))
    status = db.Column(Unicode(20), nullable=False, default="pending")
    handled_by = db.Column(Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    handled_at = db.Column(db.DateTime)

    item = db.relationship("Item", lazy="joined")
    reporter = db.relationship("User", foreign_keys=[reporter_id], lazy="joined")
