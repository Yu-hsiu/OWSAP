"""API1:2023 BOLA — 修補後的版本。

修補方式:在存取物件前,加上物件層級授權檢查——請求者只能讀自己的 id。
對應技能筆記的防禦對策:「每個用用戶端輸入去查資料庫的函數都要做授權檢查」。
（真實系統會用 RBAC / 使用者原則,並把 id 改成不可預測的 UUID;此處以最小
擁有者檢查示範核心觀念。）
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

        # === 修補:物件層級授權檢查 ===
        # 請求者只能存取屬於自己的資源;存取他人 id 一律 403,且不洩漏該 id
        # 是否存在(避免旁路資訊)。
        if requester_id != user_id:
            return jsonify({"error": "forbidden"}), 403

        target = users.get(user_id)
        if target is None:
            return jsonify({"error": "not found"}), 404
        return jsonify(target), 200

    return app


if __name__ == "__main__":
    create_app().run(port=5002)
