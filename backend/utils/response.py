from flask import jsonify


def ok(data=None, message="ok", status=200):
    return jsonify({"code": 0, "message": message, "data": data}), status


def fail(message, status=400):
    """统一错误响应：HTTP 状态码与 code 保持一致。"""
    return jsonify({"code": status, "message": message, "data": None}), status
