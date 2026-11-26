# 校园二手交易平台

校园闲置交易的课程实践项目，前后端分离：学生可发布、搜索、购买二手物品，卖家处理订单，管理员负责审核与治理。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + Vue Router + Pinia（开发端口 2064） |
| 后端 | Flask + Flask-SQLAlchemy + JWT（端口 5000） |
| 数据库 | SQL Server 2022，库名 `campus_trade`，共 11 张表 |

## 主要功能

注册登录、商品发布/搜索/筛选、下单与订单状态流转、评价与信用分、收藏、举报、站内通知、管理后台（用户封禁、商品下架、举报处理、统计）。

## 目录结构

```
backend/    Flask 接口：models 模型、routes 路由、utils 工具、tests 测试、db 建库脚本
frontend/   Vue3 前端：views 页面、components 组件、api 接口封装
start.bat / stop.bat   一键启动、停止前后端
```

## 本地运行

1. 后端
   ```bash
   pip install -r backend/requirements.txt
   # 在 backend/ 下新建 .env，填写 DB_SERVER、DB_NAME、DB_USER、DB_PASSWORD、DB_DRIVER、SECRET_KEY
   python backend/db/setup_db.py
   python backend/app.py
   ```
2. 前端
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. 浏览器访问 http://localhost:2064

## 说明

`.env`（含数据库密码）、`backend/uploads/`、`node_modules/`、`dist/` 均未纳入版本管理，克隆后需自行配置运行环境。
