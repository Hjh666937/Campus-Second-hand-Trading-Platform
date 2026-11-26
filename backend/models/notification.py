from datetime import datetime

from sqlalchemy import Identity, Integer, Unicode

from extensions import db


class Notification(db.Model):
    """站内通知表，对应 dbo.notifications。"""

    __tablename__ = "notifications"

    id = db.Column(Integer, Identity(1, 1), primary_key=True)
    user_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False)
    event = db.Column(Unicode(50), nullable=False)
    title = db.Column(Unicode(100), nullable=False)
    content = db.Column(Unicode(500))
    ref_id = db.Column(Integer)
    channel = db.Column(Unicode(20), nullable=False, default="inapp")
    status = db.Column(Unicode(20), nullable=False, default="sent")
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "event": self.event,
            "title": self.title,
            "content": self.content or "",
            "refId": self.ref_id,
            "isRead": bool(self.is_read),
            "createdAt": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else "",
        }
