"""API9:2023 庫存管理不當 — 有漏洞的版本。

漏洞點:目前版本 v2 有認證控管,但舊版 v1 端點還活著、忘了下架,而且當年沒有
認證。攻擊者不走有防護的 v2,改走沒人管的 v1,就能直接拿到敏感資料。對應技能
筆記的「舊的 /v1/ 路徑仍活躍,利用未修補版本存取敏感資料」案例。
"""

from flask import Flask, jsonify, request

from users_db import resolve_token, seed_users


def create_app():
    app = Flask(__name__)
    users = seed_users()

    # --- 目前版本 v2:有認證控管 ---
    @app.get("/api/v2/users/<int:user_id>")
    def get_user_v2(user_id):
        if resolve_token(request.headers.get("Authorization")) is None:
            return jsonify({"error": "unauthenticated"}), 401
        target = users.get(user_id)
        if target is None:
            return jsonify({"error": "not found"}), 404
        return jsonify(target), 200

    # --- 舊版 v1:忘了下架、當年沒有認證(漏洞所在)---
    @app.get("/api/v1/users/<int:user_id>")
    def get_user_v1(user_id):
        # === 漏洞:舊端點無認證,直接回傳含 ssn 的完整記錄 ===
        target = users.get(user_id)
        if target is None:
            return jsonify({"error": "not found"}), 404
        return jsonify(target), 200

    return app


if __name__ == "__main__":
    create_app().run(port=5091)
