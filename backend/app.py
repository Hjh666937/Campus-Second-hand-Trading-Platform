import os

from flask import Flask, send_from_directory
from flask_cors import CORS

from config import Config
from extensions import db
from models import User  # noqa: F401  确保模型注册到 SQLAlchemy
from routes import register_blueprints
from utils.response import fail, ok


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.json.ensure_ascii = False  # 中文直接输出，不转 \uXXXX

    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)

    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

    register_blueprints(app)

    @app.get("/api/health")
    def health():
        return ok({"status": "up"})

    @app.get("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_DIR"], filename)

    @app.errorhandler(404)
    def not_found(_):
        return fail("接口不存在", 404)

    @app.errorhandler(405)
    def method_not_allowed(_):
        return fail("请求方法不允许", 405)

    @app.errorhandler(413)
    def payload_too_large(_):
        return fail("上传内容过大，请压缩图片后重试", 413)

    @app.errorhandler(500)
    def server_error(_):
        db.session.rollback()
        return fail("服务器内部错误", 500)

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=True)
