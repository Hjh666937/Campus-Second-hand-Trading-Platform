import os
import sys
import uuid
from urllib.parse import urlparse

import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from models import (  # noqa: E402
    Conversation,
    Favorite,
    Item,
    ItemImage,
    Message,
    Notification,
    Order,
    Report,
    Review,
    User,
)


@pytest.fixture(scope="session")
def flask_app():
    application = create_app()
    application.config.update(TESTING=True)
    with application.app_context():
        yield application


@pytest.fixture()
def app(flask_app):
    return flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


class Accounts:
    """每次测试用随机账号，避免和演示数据冲突。"""

    def __init__(self):
        suffix = uuid.uuid4().hex[:8]
        self.password = "123456"
        self.seller = f"s{suffix}"
        self.buyer = f"b{suffix}"
        self.buyer2 = f"c{suffix}"
        self.admin = f"a{suffix}"

    def all(self):
        return [self.seller, self.buyer, self.buyer2, self.admin]


@pytest.fixture()
def accounts(app):
    data = Accounts()
    yield data
    cleanup_accounts(app, data.all())


def cleanup_accounts(app, account_list):
    with app.app_context():
        users = User.query.filter(User.account.in_(account_list)).all()
        user_ids = [row.id for row in users]
        if not user_ids:
            return

        conversations = Conversation.query.filter(
            db.or_(
                Conversation.buyer_id.in_(user_ids),
                Conversation.seller_id.in_(user_ids),
            )
        ).all()
        conversation_ids = [row.id for row in conversations]
        if conversation_ids:
            Message.query.filter(
                Message.conversation_id.in_(conversation_ids)
            ).delete(synchronize_session=False)
            Conversation.query.filter(
                Conversation.id.in_(conversation_ids)
            ).delete(synchronize_session=False)

        orders = Order.query.filter(
            db.or_(Order.buyer_id.in_(user_ids), Order.seller_id.in_(user_ids))
        ).all()
        order_ids = [row.id for row in orders]
        if order_ids:
            Review.query.filter(Review.order_id.in_(order_ids)).delete(
                synchronize_session=False
            )
            Order.query.filter(Order.id.in_(order_ids)).delete(
                synchronize_session=False
            )

        items = Item.query.filter(Item.seller_id.in_(user_ids)).all()
        item_ids = [row.id for row in items]
        covers = [row.cover for row in items if row.cover]

        Favorite.query.filter(Favorite.user_id.in_(user_ids)).delete(
            synchronize_session=False
        )
        Report.query.filter(Report.reporter_id.in_(user_ids)).delete(
            synchronize_session=False
        )
        Notification.query.filter(Notification.user_id.in_(user_ids)).delete(
            synchronize_session=False
        )

        if item_ids:
            ItemImage.query.filter(ItemImage.item_id.in_(item_ids)).delete(
                synchronize_session=False
            )
            Item.query.filter(Item.id.in_(item_ids)).delete(
                synchronize_session=False
            )

        User.query.filter(User.id.in_(user_ids)).delete(synchronize_session=False)
        db.session.commit()

        for url in covers:
            filename = urlparse(url).path.rsplit("/", 1)[-1]
            path = os.path.join(app.config["UPLOAD_DIR"], "items", filename)
            if os.path.isfile(path):
                os.remove(path)
