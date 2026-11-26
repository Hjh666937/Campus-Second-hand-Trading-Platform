import re

from flask import Blueprint, current_app, request
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from models import User
from utils.auth import create_token
from utils.response import fail, ok

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# 管理员保留账号，禁止注册
RESERVED_ACCOUNTS = {"admin", "administrator", "root"}

ACCOUNT_RE = re.compile(r"^[A-Za-z0-9]{3,32}$")
PASSWORD_MIN, PASSWORD_MAX = 6, 20
NICKNAME_MIN, NICKNAME_MAX = 2, 12
CAMPUS_MIN, CAMPUS_MAX = 2, 20
GENDERS = {"male", "female", "secret"}


def _clean(value):
    return value.strip() if isinstance(value, str) else ""


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}

    account = _clean(payload.get("account"))
    nickname = _clean(payload.get("nickname"))
    campus = _clean(payload.get("campus"))
    gender = _clean(payload.get("gender")) or "secret"
    password = payload.get("password") or ""
    if not isinstance(password, str):
        password = ""

    if not account:
        return fail("请输入学号", 422)
    if not ACCOUNT_RE.match(account):
        return fail("学号为 3-32 位字母或数字", 422)
    if not nickname:
        return fail("请输入昵称", 422)
    if not (NICKNAME_MIN <= len(nickname) <= NICKNAME_MAX):
        return fail(f"昵称需 {NICKNAME_MIN}-{NICKNAME_MAX} 个字", 422)
    if not campus:
        return fail("请填写校区", 422)
    if not (CAMPUS_MIN <= len(campus) <= CAMPUS_MAX):
        return fail(f"校区需 {CAMPUS_MIN}-{CAMPUS_MAX} 个字", 422)
    if gender not in GENDERS:
        return fail("性别参数不合法", 422)
    if not (PASSWORD_MIN <= len(password) <= PASSWORD_MAX):
        return fail(f"密码需 {PASSWORD_MIN}-{PASSWORD_MAX} 位", 422)

    if account.lower() in RESERVED_ACCOUNTS:
        return fail("该账号为管理员保留账号，不能注册", 403)

    if db.session.query(User.id).filter(User.account == account).first():
        return fail("该学号已注册，请直接登录", 409)

    # 角色强制为 student，忽略前端可能传来的 role
    user = User(
        account=account,
        nickname=nickname,
        campus=campus,
        gender=gender,
        password_hash=generate_password_hash(password),
        role="student",
        status="active",
        credit=100,
        must_change_password=False,
    )
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return fail("该学号已注册，请直接登录", 409)

    return ok(user.to_public_dict(), message="注册成功", status=201)


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}

    account = _clean(payload.get("account"))
    password = payload.get("password")
    remember = bool(payload.get("remember"))

    if not account or not isinstance(password, str) or not password:
        return fail("请输入账号和密码", 422)

    user = User.query.filter_by(account=account).first()
    try:
        valid = bool(user) and check_password_hash(user.password_hash, password)
    except (ValueError, TypeError):
        # 库里存的哈希格式异常时不放行，也不暴露细节
        valid = False
    if not valid:
        return fail("账号或密码错误", 401)

    if user.status != "active":
        return fail("账号已被封禁，请联系管理员", 403)

    days = (
        current_app.config["JWT_REMEMBER_DAYS"]
        if remember
        else current_app.config["JWT_DAYS"]
    )
    token = create_token(user, days)
    return ok({"token": token, "user": user.to_public_dict()}, message="登录成功")
