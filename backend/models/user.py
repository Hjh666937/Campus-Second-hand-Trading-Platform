from datetime import datetime

from sqlalchemy import Identity, Integer, Unicode

from extensions import db


class User(db.Model):
    """用户表，对应 dbo.users。"""

    __tablename__ = "users"

    id = db.Column(Integer, Identity(1, 1), primary_key=True)
    account = db.Column(Unicode(32), unique=True, nullable=False)
    password_hash = db.Column(Unicode(255), nullable=False)
    nickname = db.Column(Unicode(32), nullable=False)
    avatar = db.Column(Unicode(500))
    campus = db.Column(Unicode(50))
    gender = db.Column(Unicode(10), nullable=False, default="secret")
    credit = db.Column(Integer, nullable=False, default=100)
    role = db.Column(Unicode(10), nullable=False, default="student")
    status = db.Column(Unicode(10), nullable=False, default="active")
    must_change_password = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now,
                           onupdate=datetime.now)

    def to_public_dict(self):
        """对外返回的用户信息，永远不含密码。"""
        return {
            "id": self.id,
            "account": self.account,
            "nickname": self.nickname,
            "avatar": self.avatar,
            "campus": self.campus,
            "gender": self.gender,
            "credit": self.credit,
            "role": self.role,
        }
