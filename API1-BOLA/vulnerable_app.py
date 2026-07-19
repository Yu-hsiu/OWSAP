"""API1:2023 BOLA — 有漏洞的版本。

漏洞點:GET /api/users/<id> 只檢查「請求者有沒有登入」(認證),卻沒檢查
「請求的這筆資料是不是屬於他」(物件層級授權)。任何登入使用者都能用別人的
id 讀到別人的敏感資料(ssn),這就是 Broken Object Level Authorization。
"""

from flask import Flask, jsonify, request

from users_db import resolve_token, seed_users


def create_app():
    app = Flask(__name__)
    users = seed_users()

    @app.get("/api/users/<int:user_id>")
    def get_user(user_id):
        requester_id = resolve_token(request.headers.get("Authorization"))
        if requester_id is None:
            return jsonify({"error": "unauthenticated"}), 401

        # === 漏洞:只認證、不授權 ===
        # 這裡少了「requester_id == user_id」的擁有者檢查,直接把任何 id 的
        # 完整記錄(含 ssn)回傳給任何已登入者。
        target = users.get(user_id)
        if target is None:
            return jsonify({"error": "not found"}), 404
        return jsonify(target), 200

    return app


if __name__ == "__main__":
    create_app().run(port=5001)
