"""API3:2023 BOPLA(批量賦值)— 有漏洞的版本。

漏洞點:註冊端點把整包 request body 直接綁進使用者記錄(mass assignment),
沒有限制哪些欄位可由用戶端設定。攻擊者在 body 裡多塞一個 is_admin=true,後端
照單全收,於是註冊完就是管理員。對應技能筆記的「批量賦值提權」案例。
"""

from itertools import count

from flask import Flask, jsonify, request

from accounts_db import new_token


def create_app():
    app = Flask(__name__)
    users = {}            # user_id -> 使用者記錄
    tokens = {}           # token -> user_id
    next_id = count(1)

    @app.post("/api/register")
    def register():
        body = request.get_json(silent=True) or {}
        user_id = next(next_id)

        # === 漏洞:把整包 body 綁進記錄 ===
        # is_admin 預設 False,但緊接著用 body 覆蓋,用戶端送 is_admin=true 就贏了。
        record = {"id": user_id, "is_admin": False}
        record.update(body)

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
    create_app().run(port=5021)
