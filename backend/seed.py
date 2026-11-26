"""演示数据：卖家账号 + 16 件商品（图片下载到 uploads/items，失败则保留远程地址）。

用法：python seed.py
可重复执行：账号存在则更新资料，商品按标题去重。
"""
import os
import urllib.parse
import urllib.request
import uuid
from datetime import datetime

from werkzeug.security import generate_password_hash

from app import create_app
from extensions import db
from models import (
    Conversation,
    Favorite,
    Item,
    ItemImage,
    Message,
    Order,
    Review,
    User,
)

BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:5000")
IMAGE_API = (
    "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image"
    "?prompt={prompt}&image_size=landscape_4_3"
)

SELLERS = [
    ("20260001", "王五大", "东校区", "male", 98),
    ("20260002", "陈一鸣", "东校区", "male", 92),
    ("20260003", "周舟", "南湖校区", "female", 96),
    ("20260004", "许知远", "西校区", "male", 88),
    ("20260005", "赵一诺", "南湖校区", "female", 95),
    ("20260006", "孙可", "西校区", "female", 90),
]

ITEMS = [
    ("高等数学同济第七版 上下册", 25, "九成新", "东校区", 1, "林小满", 86, "2026-11-10",
     "大一上学期用过，书页干净，只有少量标注，可送到宿舍楼下。",
     "stack of used college calculus textbooks on a wooden desk, natural light, realistic photo"),
    ("大学英语四级真题 + 词汇书", 15, "八成新", "东校区", 1, "陈一鸣", 45, "2026-11-09",
     "四级一次过，真题只做了前两套，词汇书没有笔记。",
     "used english exam prep books and vocabulary book on a desk, realistic photo"),
    ("87 键机械键盘 红轴", 120, "九成新", "南湖校区", 2, "周舟", 132, "2026-11-11",
     "换了静音键盘闲置，红轴手感完好，键帽无磨损。",
     "compact mechanical keyboard with red switches on a clean desk, realistic product photo"),
    ("iPad 2021 64G 无线局域网版", 1350, "八成新", "西校区", 2, "许知远", 301, "2026-11-08",
     "自用一年，屏幕无划痕，电池健康 89%，带原装充电器。",
     "used tablet computer with white screen on a desk next to a notebook, realistic photo"),
    ("蓝牙耳机 入耳式 续航 24 小时", 80, "九成新", "东校区", 2, "林小满", 97, "2026-11-11",
     "买了新耳机，这副闲置，续航正常，附四副耳塞。",
     "wireless earbuds in charging case on a light background, realistic product photo"),
    ("护眼台灯 三档调光", 30, "九成新", "南湖校区", 3, "赵一诺", 28, "2026-11-07",
     "宿舍换了大灯，台灯闲置，三档调光都正常。",
     "white led desk lamp on a study desk, warm light, realistic photo"),
    ("宿舍收纳箱 大号两只", 20, "全新", "西校区", 3, "孙可", 19, "2026-11-12",
     "买多了没用上，两只一起出，可折叠收纳。",
     "two stacked plastic storage boxes in a dorm room, realistic photo"),
    ("小电煮锅 1.5L 宿舍可用", 45, "八成新", "东校区", 3, "周舟", 64, "2026-11-06",
     "毕业带不走，煮面煮粥都行，宿舍限电 800W 内可用。",
     "small electric cooking pot on a kitchen counter, realistic product photo"),
    ("斯伯丁篮球 七号", 40, "七成新", "南湖校区", 4, "陈一鸣", 52, "2026-11-05",
     "换新球了，这个还能打，气很足。",
     "used basketball on an outdoor court at sunset, realistic photo"),
    ("加厚瑜伽垫 183×61cm", 25, "九成新", "西校区", 4, "赵一诺", 33, "2026-11-10",
     "买来练了两次就吃灰，无破损，送收纳带。",
     "rolled purple yoga mat on a wooden floor, realistic photo"),
    ("二手自行车 26 寸 带车锁", 260, "八成新", "东校区", 4, "许知远", 178, "2026-11-04",
     "毕业出，链条刚上过油，带一把 U 型锁。",
     "bicycle parked outside a university dormitory, daylight, photo"),
    ("轻薄羽绒服 男款 L", 150, "九成新", "南湖校区", 5, "孙可", 41, "2026-11-09",
     "去年买的，穿过几次，无污渍无破损，L 码。",
     "black winter jacket on a hanger, product photo"),
    ("跑步鞋 42 码", 90, "七成新", "西校区", 5, "周舟", 57, "2026-11-03",
     "脚长大了穿不下，鞋底磨损轻微。",
     "pair of used running shoes on a light gray background, realistic photo"),
    ("帆布托特包 米白色", 25, "全新", "东校区", 5, "林小满", 22, "2026-11-12",
     "买重了，全新未拆吊牌。",
     "beige canvas tote bag on a chair, natural light, realistic photo"),
    ("考研英语词汇 乱序版", 18, "九成新", "东校区", 1, "陈一鸣", 73, "2026-11-08",
     "背了两遍，书角轻微卷起，内页干净。",
     "thick english vocabulary book with pen on a library table, realistic photo"),
    ("24 寸显示器 1080P", 380, "八成新", "南湖校区", 2, "许知远", 156, "2026-11-07",
     "换了更大的屏，这台闲置，无坏点，附 DP 线。",
     "24 inch computer monitor on a desk in a dorm room, realistic photo"),
]

# 演示账号自己发布的商品，用来展示「我卖出的」与卖家主页的已售记录
DEMO_ACCOUNT = "20261116"

DEMO_ITEMS = [
    ("宿舍静音小风扇 三档", 25, "九成新", "东校区", 3, "2026-11-08",
     "夏天买的，宿舍有空调用不上了，三档风力都正常。",
     "Second-hand marketplace product photo: a small white three-speed desktop fan sitting on a dormitory desk next to notebooks, realistic photography, natural daylight"),
    ("考研政治真题套装 2026", 30, "八成新", "东校区", 1, "2026-11-05",
     "考研结束出，题目做了一半，附错题笔记。",
     "Second-hand marketplace product photo: a stack of Chinese postgraduate exam preparation workbooks with handwritten study notes and a pen on a wooden desk, realistic photography, warm indoor light"),
]

# order_no, 商品标题, 买家账号, 卖家账号, 状态, 创建日期, 完成日期, 评价(星级, 内容, 日期)
ORDERS = [
    ("C202611120001", "大学英语四级真题 + 词汇书", "20261116", "20260002", "completed",
     "2026-11-12", "2026-11-12", (5, "书保存得很干净，卖家还送到宿舍楼下，交易很顺利。", "2026-11-12")),
    ("C202611140002", "护眼台灯 三档调光", "20261116", "20260005", "pending",
     "2026-11-14", None, None),
    ("C202611130003", "宿舍静音小风扇 三档", "20260003", "20261116", "pending",
     "2026-11-13", None, None),
    ("C202611100004", "考研政治真题套装 2026", "20260006", "20261116", "completed",
     "2026-11-10", "2026-11-10", (5, "笔记很用心，卖家人也很好，推荐。", "2026-11-10")),
    ("C202611090005", "高等数学同济第七版 上下册", "20260002", "20260001", "completed",
     "2026-11-09", "2026-11-09", (5, "教材很新，价格实惠，沟通顺畅。", "2026-11-09")),
]


def download_cover(prompt, upload_dir):
    """下载封面图到 uploads/items，失败返回远程地址。"""
    remote = IMAGE_API.format(prompt=urllib.parse.quote(prompt))
    folder = os.path.join(upload_dir, "items")
    os.makedirs(folder, exist_ok=True)
    try:
        with urllib.request.urlopen(remote, timeout=60) as resp:
            content = resp.read()
        if len(content) < 1024:
            raise ValueError("图片内容为空")
        filename = f"{uuid.uuid4().hex}.jpg"
        with open(os.path.join(folder, filename), "wb") as fp:
            fp.write(content)
        return f"{BASE_URL.rstrip('/')}/uploads/items/{filename}"
    except Exception as error:  # noqa: BLE001 网络失败不影响入库
        print(f"    图片下载失败，保留远程地址：{error}")
        return remote


def main():
    app = create_app()
    with app.app_context():
        seller_ids = {}
        for account, nickname, campus, gender, credit in SELLERS:
            user = User.query.filter_by(account=account).first()
            if not user:
                user = User(
                    account=account,
                    password_hash=generate_password_hash("123456"),
                    nickname=nickname,
                    campus=campus,
                    gender=gender,
                    credit=credit,
                    role="student",
                    status="active",
                )
                db.session.add(user)
                db.session.flush()
                print(f"创建卖家 {nickname}（{account} / 123456）")
            seller_ids[nickname] = user.id
        db.session.commit()

        for title, price, condition, campus, category_id, seller, views, date, desc, prompt in ITEMS:
            exists = Item.query.filter_by(title=title).first()
            if exists:
                print(f"跳过已存在：{title}")
                continue

            cover = download_cover(prompt, app.config["UPLOAD_DIR"])
            item = Item(
                seller_id=seller_ids[seller],
                category_id=category_id,
                title=title,
                description=desc,
                price=price,
                condition=condition,
                campus=campus,
                cover=cover,
                status="on_sale",
                view_count=views,
                created_at=datetime.strptime(date, "%Y-%m-%d"),
                updated_at=datetime.strptime(date, "%Y-%m-%d"),
            )
            db.session.add(item)
            db.session.flush()
            db.session.add(ItemImage(item_id=item.id, url=cover, sort=0))
            print(f"写入商品：{title}")

        db.session.commit()

        demo = User.query.filter_by(account=DEMO_ACCOUNT).first()
        if not demo:
            print(f"未找到演示账号 {DEMO_ACCOUNT}，跳过演示订单")
        else:
            for title, price, condition, campus, category_id, date, desc, prompt in DEMO_ITEMS:
                if Item.query.filter_by(title=title).first():
                    print(f"跳过已存在：{title}")
                    continue
                cover = download_cover(prompt, app.config["UPLOAD_DIR"])
                item = Item(
                    seller_id=demo.id,
                    category_id=category_id,
                    title=title,
                    description=desc,
                    price=price,
                    condition=condition,
                    campus=campus,
                    cover=cover,
                    status="on_sale",
                    view_count=0,
                    created_at=datetime.strptime(date, "%Y-%m-%d"),
                    updated_at=datetime.strptime(date, "%Y-%m-%d"),
                )
                db.session.add(item)
                db.session.flush()
                db.session.add(ItemImage(item_id=item.id, url=cover, sort=0))
                print(f"写入演示商品：{title}")
            db.session.commit()

            for order_no, item_title, buyer_account, seller_account, status, created, finished, review in ORDERS:
                item = Item.query.filter_by(title=item_title).first()
                buyer = User.query.filter_by(account=buyer_account).first()
                seller = User.query.filter_by(account=seller_account).first()
                if not (item and buyer and seller):
                    print(f"跳过订单 {order_no}：关联的商品或用户不存在")
                    continue
                if Order.query.filter_by(order_no=order_no).first():
                    print(f"跳过已存在订单：{order_no}")
                    continue

                order = Order(
                    order_no=order_no,
                    item_id=item.id,
                    buyer_id=buyer.id,
                    seller_id=seller.id,
                    price=item.price,
                    status=status,
                    created_at=datetime.strptime(created, "%Y-%m-%d"),
                    finished_at=datetime.strptime(finished, "%Y-%m-%d") if finished else None,
                )
                db.session.add(order)
                db.session.flush()

                if status == "completed":
                    item.status = "sold"
                    if review:
                        rating, content, date = review
                        db.session.add(Review(
                            order_id=order.id,
                            item_id=item.id,
                            reviewer_id=buyer.id,
                            target_id=seller.id,
                            rating=rating,
                            content=content,
                            created_at=datetime.strptime(date, "%Y-%m-%d"),
                        ))
                print(f"写入订单：{order_no} {item_title}")

        # 演示会话与收藏：买家（演示账号）咨询蓝牙耳机
        demo_user = User.query.filter_by(account=DEMO_ACCOUNT).first()
        chat_item = Item.query.filter_by(title="蓝牙耳机 入耳式 续航 24 小时").first()
        chat_seller = User.query.filter_by(account="20260001").first()
        if demo_user and chat_item and chat_seller:
            conversation = Conversation.query.filter_by(
                item_id=chat_item.id, buyer_id=demo_user.id
            ).first()
            if not conversation:
                conversation = Conversation(
                    item_id=chat_item.id,
                    buyer_id=demo_user.id,
                    seller_id=chat_seller.id,
                    last_message="在的，明天中午图书馆门口可以吗？",
                    last_at=datetime(2026, 11, 15, 12, 30),
                    buyer_unread=1,
                    created_at=datetime(2026, 11, 15, 12, 0),
                )
                db.session.add(conversation)
                db.session.flush()
                db.session.add_all([
                    Message(
                        conversation_id=conversation.id,
                        sender_id=demo_user.id,
                        content="同学，耳机还在吗？",
                        is_read=True,
                        created_at=datetime(2026, 11, 15, 12, 0),
                    ),
                    Message(
                        conversation_id=conversation.id,
                        sender_id=chat_seller.id,
                        content="在的，明天中午图书馆门口可以吗？",
                        is_read=False,
                        created_at=datetime(2026, 11, 15, 12, 30),
                    ),
                ])
                print("写入演示会话与消息")

            favorite = Favorite.query.filter_by(
                user_id=demo_user.id, item_id=chat_item.id
            ).first()
            if not favorite:
                db.session.add(Favorite(user_id=demo_user.id, item_id=chat_item.id))
                print("写入演示收藏")

        db.session.commit()
        print(
            f"\n完成：商品 {Item.query.count()} 件，订单 {Order.query.count()} 笔，"
            f"评价 {Review.query.count()} 条，会话 {Conversation.query.count()} 个，"
            f"卖家账号 {len(SELLERS)} 个"
        )


if __name__ == "__main__":
    main()
