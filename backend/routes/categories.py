from flask import Blueprint

from models import Category
from utils.response import ok

categories_bp = Blueprint("categories", __name__, url_prefix="/api/categories")


@categories_bp.get("", strict_slashes=False)
def list_categories():
    """商品分类，发布页与首页筛选共用。"""
    rows = (
        Category.query.filter(Category.is_active == True)  # noqa: E712
        .order_by(Category.sort.asc(), Category.id.asc())
        .all()
    )
    return ok([{"id": row.id, "name": row.name} for row in rows])
