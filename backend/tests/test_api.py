"""核心接口冒烟测试。

运行：
    cd backend
    python -m pytest tests -q

测试使用真实 SQL Server 数据库（.env 配置），每个用例用随机账号，
结束后自动清理账号及关联数据、上传图片。
"""

from werkzeug.security import generate_password_hash

from extensions import db
from models import User

PNG = (
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
    "AAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


def register(client, account, nickname):
    return client.post("/api/auth/register", json={
        "account": account,
        "password": "123456",
        "nickname": nickname,
        "campus": "东校区",
        "gender": "secret",
    })


def login(client, account, password="123456"):
    response = client.post("/api/auth/login", json={
        "account": account,
        "password": password,
    })
    payload = response.get_json()
    assert response.status_code == 200, payload
    return payload["data"]["token"], payload["data"]["user"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def create_item(client, token, title="测试商品", description="这是用于接口测试的商品描述"):
    response = client.post("/api/items", json={
        "title": title,
        "categoryId": 1,
        "price": 12.5,
        "condition": "九成新",
        "campus": "东校区",
        "description": description,
        "images": [PNG],
    }, headers=auth(token))
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def make_admin(app, accounts):
    with app.app_context():
        db.session.add(User(
            account=accounts.admin,
            password_hash=generate_password_hash("123456"),
            nickname="测试管理员",
            campus="东校区",
            gender="secret",
            role="admin",
            status="active",
            credit=100,
        ))
        db.session.commit()


def test_register_login_and_profile(client, accounts):
    assert register(client, accounts.seller, "测试卖家").status_code == 201
    token, user = login(client, accounts.seller)
    assert user["role"] == "student"

    me = client.get("/api/users/me", headers=auth(token))
    assert me.status_code == 200
    assert me.get_json()["data"]["account"] == accounts.seller


def test_item_search_favorite(client, accounts):
    register(client, accounts.seller, "测试卖家")
    seller_token, seller = login(client, accounts.seller)
    item = create_item(client, seller_token, description="描述里包含限定检索词")

    register(client, accounts.buyer, "测试买家")
    buyer_token, _ = login(client, accounts.buyer)

    found = client.get("/api/items", query_string={"keyword": "限定检索词"})
    assert found.status_code == 200
    assert [row["id"] for row in found.get_json()["data"]["list"]] == [item["id"]]

    assert client.post("/api/favorites", json={"itemId": item["id"]},
                       headers=auth(buyer_token)).get_json()["data"]["favorite"] is True
    assert client.get("/api/favorites/check", query_string={"itemId": item["id"]},
                      headers=auth(buyer_token)).get_json()["data"] is True
    assert len(client.get("/api/favorites", headers=auth(buyer_token)).get_json()["data"]) == 1

    client.post("/api/favorites", json={"itemId": item["id"]}, headers=auth(buyer_token))
    assert client.get("/api/favorites", headers=auth(buyer_token)).get_json()["data"] == []


def test_order_review_and_notifications(client, accounts):
    register(client, accounts.seller, "测试卖家")
    seller_token, seller = login(client, accounts.seller)
    item = create_item(client, seller_token)

    register(client, accounts.buyer, "测试买家")
    buyer_token, _ = login(client, accounts.buyer)

    created = client.post("/api/orders", json={"itemId": item["id"]},
                          headers=auth(buyer_token))
    assert created.status_code == 201, created.get_json()
    order_id = created.get_json()["data"]["id"]

    seller_notify = client.get("/api/notifications", headers=auth(seller_token)).get_json()["data"]
    assert seller_notify["unread"] >= 1
    assert seller_notify["list"][0]["title"] == "收到新订单"

    assert client.patch(f"/api/orders/{order_id}/status", json={"status": "confirmed"},
                        headers=auth(seller_token)).status_code == 200
    buyer_notify = client.get("/api/notifications", headers=auth(buyer_token)).get_json()["data"]
    assert buyer_notify["list"][0]["title"] == "卖家已确认订单"

    # 卖家不能替买家确认收货
    assert client.patch(f"/api/orders/{order_id}/status", json={"status": "completed"},
                        headers=auth(seller_token)).status_code == 403
    assert client.patch(f"/api/orders/{order_id}/status", json={"status": "completed"},
                        headers=auth(buyer_token)).status_code == 200

    detail = client.get(f"/api/items/{item['id']}").get_json()["data"]
    assert detail["status"] == "sold"

    review = client.post(f"/api/orders/{order_id}/review",
                         json={"rating": 4, "content": "东西不错"},
                         headers=auth(buyer_token))
    assert review.status_code == 201, review.get_json()
    assert review.get_json()["data"]["content"] == "东西不错"

    profile = client.get(f"/api/users/id/{seller['id']}").get_json()["data"]
    assert profile["credit"] == 99
    assert profile["reviewCount"] == 1
    assert profile["reviews"][0]["content"] == "东西不错"


def test_chat_flow(client, accounts):
    register(client, accounts.seller, "测试卖家")
    seller_token, _ = login(client, accounts.seller)
    item = create_item(client, seller_token)

    register(client, accounts.buyer, "测试买家")
    buyer_token, _ = login(client, accounts.buyer)

    opened = client.post("/api/conversations", json={"itemId": item["id"]},
                         headers=auth(buyer_token))
    assert opened.status_code == 200
    conversation_id = opened.get_json()["data"]["id"]

    # 卖家不能和自己聊天
    assert client.post("/api/conversations", json={"itemId": item["id"]},
                       headers=auth(seller_token)).status_code == 400

    sent = client.post(f"/api/conversations/{conversation_id}/messages",
                       json={"content": "你好，还在吗？"}, headers=auth(buyer_token))
    assert sent.status_code == 201

    seller_list = client.get("/api/conversations", headers=auth(seller_token)).get_json()["data"]
    assert seller_list[0]["unread"] == 1
    assert seller_list[0]["peerNickname"] == "测试买家"

    messages = client.get(f"/api/conversations/{conversation_id}/messages",
                          headers=auth(seller_token)).get_json()["data"]
    assert len(messages) == 1 and messages[0]["content"] == "你好，还在吗？"

    client.post(f"/api/conversations/{conversation_id}/read", headers=auth(seller_token))
    unread = client.get("/api/conversations/unread-count", headers=auth(seller_token))
    assert unread.get_json()["data"] == 0


def test_admin_permissions_and_reports(client, app, accounts):
    register(client, accounts.seller, "测试卖家")
    seller_token, _ = login(client, accounts.seller)
    item = create_item(client, seller_token)

    register(client, accounts.buyer, "测试买家")
    buyer_token, _ = login(client, accounts.buyer)

    make_admin(app, accounts)
    admin_token, _ = login(client, accounts.admin)

    # 管理员不能发布商品 / 下单
    assert client.post("/api/items", json={
        "title": "管理员商品", "categoryId": 1, "price": 1,
        "condition": "全新", "campus": "东校区", "description": "x", "images": [PNG],
    }, headers=auth(admin_token)).status_code == 403
    assert client.post("/api/orders", json={"itemId": item["id"]},
                       headers=auth(admin_token)).status_code == 403

    stats = client.get("/api/admin/stats", headers=auth(admin_token))
    assert stats.status_code == 200
    assert stats.get_json()["data"]["userCount"] >= 2

    users = client.get("/api/admin/users", headers=auth(admin_token)).get_json()["data"]
    assert any(row["account"] == accounts.seller for row in users)

    # 封禁后无法登录
    assert client.patch(f"/api/admin/users/{accounts.seller}/status",
                        json={"status": "banned"},
                        headers=auth(admin_token)).status_code == 200
    blocked = client.post("/api/auth/login", json={
        "account": accounts.seller, "password": "123456",
    })
    assert blocked.status_code == 403
    client.patch(f"/api/admin/users/{accounts.seller}/status",
                 json={"status": "active"}, headers=auth(admin_token))

    # 重置密码为账号后 6 位
    assert client.patch(f"/api/admin/users/{accounts.seller}/password/reset",
                        headers=auth(admin_token)).status_code == 200
    login(client, accounts.seller, accounts.seller[-6:])

    # 举报提交与后台处理
    report = client.post("/api/reports", json={
        "itemId": item["id"], "reason": "虚假信息", "detail": "测试举报",
    }, headers=auth(buyer_token))
    assert report.status_code == 201

    reports = client.get("/api/admin/reports", headers=auth(admin_token)).get_json()["data"]
    assert reports[0]["reason"] == "虚假信息"
    assert reports[0]["status"] == "pending"

    report_id = reports[0]["id"]
    assert client.patch(f"/api/admin/reports/{report_id}", json={"status": "handled"},
                        headers=auth(admin_token)).status_code == 200
    handled = client.get("/api/admin/reports", headers=auth(admin_token)).get_json()["data"]
    assert handled[0]["status"] == "handled"
