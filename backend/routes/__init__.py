from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.categories import categories_bp
from routes.chat import chat_bp
from routes.favorites import favorites_bp
from routes.items import items_bp
from routes.notifications import notifications_bp
from routes.orders import orders_bp, reviews_bp
from routes.reports import reports_bp
from routes.users import users_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(favorites_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(admin_bp)
