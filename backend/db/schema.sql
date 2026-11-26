/* ============================================================
   校园二手交易平台 —— SQL Server 建库建表脚本
   数据库：campus_trade
   用法：在 SSMS 中打开本文件 -> 连接到 DESKTOP-MIASER (sa)
        -> 执行（F5）。脚本可重复执行，已存在的对象会跳过。
   说明：所有时间字段用 DATETIME2，中文用 NVARCHAR，金额用 DECIMAL。
   ============================================================ */

IF DB_ID(N'campus_trade') IS NULL
    EXEC(N'CREATE DATABASE campus_trade');
GO

USE campus_trade;
GO

/* ---------- 1. 用户 ---------- */
IF OBJECT_ID(N'dbo.users', N'U') IS NULL
CREATE TABLE dbo.users (
    id                   INT IDENTITY(1,1) NOT NULL,
    account              NVARCHAR(32)  NOT NULL,              -- 学号 / 管理员账号
    password_hash        NVARCHAR(255) NOT NULL,              -- 只存哈希，不存明文
    nickname             NVARCHAR(32)  NOT NULL,
    avatar               NVARCHAR(500) NULL,                  -- 头像 URL
    campus               NVARCHAR(50)  NULL,                  -- 校区，自由填写
    gender               NVARCHAR(10)  NOT NULL CONSTRAINT DF_users_gender DEFAULT N'secret',
    credit               INT           NOT NULL CONSTRAINT DF_users_credit DEFAULT 100,
    role                 NVARCHAR(10)  NOT NULL CONSTRAINT DF_users_role   DEFAULT N'student',
    status               NVARCHAR(10)  NOT NULL CONSTRAINT DF_users_status DEFAULT N'active',
    must_change_password BIT           NOT NULL CONSTRAINT DF_users_mustcp DEFAULT 0,
    created_at           DATETIME2(0)  NOT NULL CONSTRAINT DF_users_created DEFAULT SYSDATETIME(),
    updated_at           DATETIME2(0)  NOT NULL CONSTRAINT DF_users_updated DEFAULT SYSDATETIME(),
    CONSTRAINT PK_users PRIMARY KEY (id),
    CONSTRAINT UQ_users_account UNIQUE (account),
    CONSTRAINT CK_users_gender CHECK (gender IN (N'male', N'female', N'secret')),
    CONSTRAINT CK_users_role   CHECK (role   IN (N'student', N'admin')),
    CONSTRAINT CK_users_status CHECK (status IN (N'active', N'banned'))
);
GO

/* ---------- 2. 分类 ---------- */
IF OBJECT_ID(N'dbo.categories', N'U') IS NULL
CREATE TABLE dbo.categories (
    id         INT IDENTITY(1,1) NOT NULL,
    name       NVARCHAR(30)  NOT NULL,
    sort       INT           NOT NULL CONSTRAINT DF_categories_sort DEFAULT 0,
    is_active  BIT           NOT NULL CONSTRAINT DF_categories_active DEFAULT 1,
    created_at DATETIME2(0)  NOT NULL CONSTRAINT DF_categories_created DEFAULT SYSDATETIME(),
    CONSTRAINT PK_categories PRIMARY KEY (id),
    CONSTRAINT UQ_categories_name UNIQUE (name)
);
GO

/* ---------- 3. 商品 ---------- */
IF OBJECT_ID(N'dbo.items', N'U') IS NULL
CREATE TABLE dbo.items (
    id           INT IDENTITY(1,1) NOT NULL,
    seller_id    INT            NOT NULL,
    category_id  INT            NOT NULL,
    title        NVARCHAR(80)   NOT NULL,
    description  NVARCHAR(MAX)  NULL,
    price        DECIMAL(10,2)  NOT NULL,
    condition    NVARCHAR(20)   NOT NULL,                     -- 成色：全新 / 九成新 / 八成新 ...
    campus       NVARCHAR(50)   NOT NULL,
    cover        NVARCHAR(500)  NULL,                          -- 封面图 URL
    status       NVARCHAR(20)   NOT NULL CONSTRAINT DF_items_status DEFAULT N'on_sale',
    view_count   INT            NOT NULL CONSTRAINT DF_items_view DEFAULT 0,
    is_deleted   BIT            NOT NULL CONSTRAINT DF_items_deleted DEFAULT 0,
    created_at   DATETIME2(0)   NOT NULL CONSTRAINT DF_items_created DEFAULT SYSDATETIME(),
    updated_at   DATETIME2(0)   NOT NULL CONSTRAINT DF_items_updated DEFAULT SYSDATETIME(),
    CONSTRAINT PK_items PRIMARY KEY (id),
    CONSTRAINT FK_items_seller   FOREIGN KEY (seller_id)   REFERENCES dbo.users (id),
    CONSTRAINT FK_items_category FOREIGN KEY (category_id) REFERENCES dbo.categories (id),
    CONSTRAINT CK_items_status CHECK (status IN (N'on_sale', N'locked', N'sold', N'off_shelf')),
    CONSTRAINT CK_items_price  CHECK (price > 0)
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_items_list' AND object_id = OBJECT_ID(N'dbo.items'))
    CREATE INDEX IX_items_list ON dbo.items (status, is_deleted, category_id, created_at DESC, id DESC);
GO

/* ---------- 4. 商品图片 ---------- */
IF OBJECT_ID(N'dbo.item_images', N'U') IS NULL
CREATE TABLE dbo.item_images (
    id       INT IDENTITY(1,1) NOT NULL,
    item_id  INT           NOT NULL,
    url      NVARCHAR(500) NOT NULL,
    sort     INT           NOT NULL CONSTRAINT DF_item_images_sort DEFAULT 0,
    CONSTRAINT PK_item_images PRIMARY KEY (id),
    CONSTRAINT FK_item_images_item FOREIGN KEY (item_id) REFERENCES dbo.items (id) ON DELETE CASCADE
);
GO

/* ---------- 5. 收藏 ---------- */
IF OBJECT_ID(N'dbo.favorites', N'U') IS NULL
CREATE TABLE dbo.favorites (
    id         INT IDENTITY(1,1) NOT NULL,
    user_id    INT          NOT NULL,
    item_id    INT          NOT NULL,
    created_at DATETIME2(0) NOT NULL CONSTRAINT DF_favorites_created DEFAULT SYSDATETIME(),
    CONSTRAINT PK_favorites PRIMARY KEY (id),
    CONSTRAINT UQ_favorites_user_item UNIQUE (user_id, item_id),
    CONSTRAINT FK_favorites_user FOREIGN KEY (user_id) REFERENCES dbo.users (id),
    CONSTRAINT FK_favorites_item FOREIGN KEY (item_id) REFERENCES dbo.items (id)
);
GO

/* ---------- 6. 订单 ---------- */
IF OBJECT_ID(N'dbo.orders', N'U') IS NULL
CREATE TABLE dbo.orders (
    id          INT IDENTITY(1,1) NOT NULL,
    order_no    NVARCHAR(32)   NOT NULL,
    item_id     INT            NOT NULL,
    buyer_id    INT            NOT NULL,
    seller_id   INT            NOT NULL,
    price       DECIMAL(10,2)  NOT NULL,
    status      NVARCHAR(20)   NOT NULL CONSTRAINT DF_orders_status DEFAULT N'pending',
    created_at  DATETIME2(0)   CONSTRAINT DF_orders_created  DEFAULT SYSDATETIME(),
    updated_at  DATETIME2(0)   CONSTRAINT DF_orders_updated  DEFAULT SYSDATETIME(),
    finished_at DATETIME2(0)   NULL,
    cancelled_at DATETIME2(0)  NULL,
    CONSTRAINT PK_orders PRIMARY KEY (id),
    CONSTRAINT UQ_orders_no UNIQUE (order_no),
    CONSTRAINT FK_orders_item   FOREIGN KEY (item_id)   REFERENCES dbo.items (id),
    CONSTRAINT FK_orders_buyer  FOREIGN KEY (buyer_id)  REFERENCES dbo.users (id),
    CONSTRAINT FK_orders_seller FOREIGN KEY (seller_id) REFERENCES dbo.users (id),
    CONSTRAINT CK_orders_status CHECK (status IN (N'pending', N'confirmed', N'completed', N'cancelled'))
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_orders_buyer' AND object_id = OBJECT_ID(N'dbo.orders'))
    CREATE INDEX IX_orders_buyer ON dbo.orders (buyer_id, status, created_at DESC);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_orders_seller' AND object_id = OBJECT_ID(N'dbo.orders'))
    CREATE INDEX IX_orders_seller ON dbo.orders (seller_id, status, created_at DESC);
GO

/* ---------- 7. 交易评价（一单一评） ---------- */
IF OBJECT_ID(N'dbo.reviews', N'U') IS NULL
CREATE TABLE dbo.reviews (
    id         INT IDENTITY(1,1) NOT NULL,
    order_id   INT           NOT NULL,
    item_id    INT           NOT NULL,
    reviewer_id INT          NOT NULL,                      -- 评价人
    target_id  INT           NOT NULL,                      -- 被评价人
    rating     TINYINT       NOT NULL,
    content    NVARCHAR(500) NULL,
    created_at DATETIME2(0)  NOT NULL CONSTRAINT DF_reviews_created DEFAULT SYSDATETIME(),
    CONSTRAINT PK_reviews PRIMARY KEY (id),
    CONSTRAINT UQ_reviews_order UNIQUE (order_id),
    CONSTRAINT FK_reviews_order FOREIGN KEY (order_id) REFERENCES dbo.orders (id),
    CONSTRAINT FK_reviews_item  FOREIGN KEY (item_id)  REFERENCES dbo.items (id),
    CONSTRAINT CK_reviews_rating CHECK (rating BETWEEN 1 AND 5)
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_reviews_target' AND object_id = OBJECT_ID(N'dbo.reviews'))
    CREATE INDEX IX_reviews_target ON dbo.reviews (target_id, created_at DESC);
GO

/* ---------- 8. 举报 ---------- */
IF OBJECT_ID(N'dbo.reports', N'U') IS NULL
CREATE TABLE dbo.reports (
    id           INT IDENTITY(1,1) NOT NULL,
    item_id      INT           NOT NULL,
    reporter_id  INT           NOT NULL,
    reason       NVARCHAR(50)  NOT NULL,
    detail       NVARCHAR(500) NULL,
    status       NVARCHAR(20)  NOT NULL CONSTRAINT DF_reports_status DEFAULT N'pending',
    handled_by   INT           NULL,
    created_at   DATETIME2(0)  NOT NULL CONSTRAINT DF_reports_created DEFAULT SYSDATETIME(),
    handled_at   DATETIME2(0)  NULL,
    CONSTRAINT PK_reports PRIMARY KEY (id),
    CONSTRAINT FK_reports_item     FOREIGN KEY (item_id)     REFERENCES dbo.items (id),
    CONSTRAINT FK_reports_reporter FOREIGN KEY (reporter_id) REFERENCES dbo.users (id),
    CONSTRAINT FK_reports_handler  FOREIGN KEY (handled_by)  REFERENCES dbo.users (id),
    CONSTRAINT CK_reports_status CHECK (status IN (N'pending', N'handled', N'rejected'))
);
GO

/* ---------- 9. 会话 ---------- */
IF OBJECT_ID(N'dbo.conversations', N'U') IS NULL
CREATE TABLE dbo.conversations (
    id            INT IDENTITY(1,1) NOT NULL,
    item_id       INT           NOT NULL,
    buyer_id      INT           NOT NULL,
    seller_id     INT           NOT NULL,
    last_message  NVARCHAR(200) NULL,
    last_at       DATETIME2(0)  NULL,
    buyer_unread  INT           NOT NULL CONSTRAINT DF_conv_buyer_unread  DEFAULT 0,
    seller_unread INT           NOT NULL CONSTRAINT DF_conv_seller_unread DEFAULT 0,
    created_at    DATETIME2(0)  NOT NULL CONSTRAINT DF_conv_created DEFAULT SYSDATETIME(),
    CONSTRAINT PK_conversations PRIMARY KEY (id),
    CONSTRAINT UQ_conv_item_buyer UNIQUE (item_id, buyer_id),
    CONSTRAINT FK_conv_item   FOREIGN KEY (item_id)   REFERENCES dbo.items (id),
    CONSTRAINT FK_conv_buyer  FOREIGN KEY (buyer_id)  REFERENCES dbo.users (id),
    CONSTRAINT FK_conv_seller FOREIGN KEY (seller_id) REFERENCES dbo.users (id)
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_conv_seller' AND object_id = OBJECT_ID(N'dbo.conversations'))
    CREATE INDEX IX_conv_seller ON dbo.conversations (seller_id, last_at DESC);
GO

/* ---------- 10. 消息 ---------- */
IF OBJECT_ID(N'dbo.messages', N'U') IS NULL
CREATE TABLE dbo.messages (
    id              INT IDENTITY(1,1) NOT NULL,
    conversation_id INT           NOT NULL,
    sender_id       INT           NOT NULL,
    type            NVARCHAR(10)  NOT NULL CONSTRAINT DF_msg_type DEFAULT N'text',
    content         NVARCHAR(MAX) NOT NULL,
    is_read         BIT           NOT NULL CONSTRAINT DF_msg_read DEFAULT 0,
    created_at      DATETIME2(0)  NOT NULL CONSTRAINT DF_msg_created DEFAULT SYSDATETIME(),
    CONSTRAINT PK_messages PRIMARY KEY (id),
    CONSTRAINT FK_msg_conv   FOREIGN KEY (conversation_id) REFERENCES dbo.conversations (id) ON DELETE CASCADE,
    CONSTRAINT FK_msg_sender FOREIGN KEY (sender_id)       REFERENCES dbo.users (id),
    CONSTRAINT CK_msg_type CHECK (type IN (N'text', N'image'))
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_msg_conv' AND object_id = OBJECT_ID(N'dbo.messages'))
    CREATE INDEX IX_msg_conv ON dbo.messages (conversation_id, created_at DESC, id DESC);
GO

/* ---------- 11. 通知（消息渠道预留） ---------- */
IF OBJECT_ID(N'dbo.notifications', N'U') IS NULL
CREATE TABLE dbo.notifications (
    id         INT IDENTITY(1,1) NOT NULL,
    user_id    INT           NOT NULL,
    event      NVARCHAR(50)  NOT NULL,                       -- order_created / order_completed ...
    title      NVARCHAR(100) NOT NULL,
    content    NVARCHAR(500) NULL,
    ref_id     INT           NULL,                            -- 关联业务 id
    channel    NVARCHAR(20)  NOT NULL CONSTRAINT DF_notify_channel DEFAULT N'inapp',
    status     NVARCHAR(20)  NOT NULL CONSTRAINT DF_notify_status  DEFAULT N'sent',
    is_read    BIT           NOT NULL CONSTRAINT DF_notify_read    DEFAULT 0,
    created_at DATETIME2(0)  NOT NULL CONSTRAINT DF_notify_created DEFAULT SYSDATETIME(),
    CONSTRAINT PK_notifications PRIMARY KEY (id),
    CONSTRAINT FK_notify_user FOREIGN KEY (user_id) REFERENCES dbo.users (id),
    CONSTRAINT CK_notify_channel CHECK (channel IN (N'inapp', N'email', N'sms')),
    CONSTRAINT CK_notify_status  CHECK (status  IN (N'pending', N'sent', N'failed'))
);
GO

/* ---------- 基础数据：分类 ---------- */
IF NOT EXISTS (SELECT 1 FROM dbo.categories)
BEGIN
    INSERT INTO dbo.categories (name, sort) VALUES
        (N'教材书籍', 1),
        (N'数码电子', 2),
        (N'生活用品', 3),
        (N'运动户外', 4),
        (N'衣物鞋包', 5);
END
GO
