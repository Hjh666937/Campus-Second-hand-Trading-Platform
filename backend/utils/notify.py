from extensions import db
from models import Notification


def notify(user_id, event, title, content=None, ref_id=None):
    """写入一条站内通知，随业务事务一起提交。"""
    if not user_id:
        return
    db.session.add(Notification(
        user_id=user_id,
        event=event,
        title=title,
        content=content,
        ref_id=ref_id,
    ))
