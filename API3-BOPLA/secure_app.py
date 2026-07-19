"""API3:2023 BOPLA(批量賦值)— 修補後的版本。

修補方式:註冊時只從 body 取「白名單」欄位(name/email/password),敏感屬性
is_admin 一律由後端決定、不接受用戶端輸入。對應技能筆記的防禦對策:「避免把
用戶端輸入自動綁到內部物件,僅允許該被更新的屬性」。
"""

from itertools import count

from flask import Flask, jsonify, request

from accounts_db import ALLOWED_REGISTRATION_FIELDS, new_token


def create_app():
    app = Flask(__name__)
    users = {}
    tokens = {}
    next_id = count(1)

    @app.post("/api/register")
    def register():
        body = request.get_json(silent=True) or {}
        user_id = next(next_id)

        # === 修補:只挑白名單欄位,is_admin 恆由後端設定 ===
        record = {key: body[key] for key in ALLOWED_REGISTRATION_FIELDS if key in body}
        record["id"] = user_id
        record["is_admin"] = False  # 權限不接受用戶端輸入

        token = new_token()
        users[user_id] = record
        tokens[token] = user_id
        return jsonify({"token": token, "is_admin": record["is_admin"]}), 201

    @app.get("/api/admin/stats")
    def admin_stats():
        token = (request.headers.get("Authorization") or "").removeprefix("Bearer ").strip()
        user_id = tokens.get(token)
        if user_id is None:
            return jsonify({"error": "unauthenticated"}), 401
        if not users[user_id].get("is_admin"):
            return jsonify({"error": "forbidden"}), 403
        return jsonify({"secret_stats": "全體使用者機密統計資料"}), 200

    return app


if __name__ == "__main__":
    create_app().run(port=5022)
