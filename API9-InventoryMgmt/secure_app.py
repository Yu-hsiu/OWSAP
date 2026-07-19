"""API9:2023 庫存管理不當 — 修補後的版本。

修補方式:盤點並退役舊版本——v1 正式下架(回 410 Gone),只保留有認證控管的 v2。
對應技能筆記的防禦對策:「盤點所有 API 主機並記錄版本;對所有暴露的 API 版本
(不限於目前的生產版)實施控管」。(除了下架,另一種做法是把 v1 補上與 v2 相同的
控管;此處以下架示範最乾淨的退役方式。)
"""

from flask import Flask, jsonify, request

from users_db import resolve_token, seed_users


def create_app():
    app = Flask(__name__)
    users = seed_users()

    @app.get("/api/v2/users/<int:user_id>")
    def get_user_v2(user_id):
        if resolve_token(request.headers.get("Authorization")) is None:
            return jsonify({"error": "unauthenticated"}), 401
        target = users.get(user_id)
        if target is None:
            return jsonify({"error": "not found"}), 404
        return jsonify(target), 200

    # === 修補:舊版 v1 已退役,一律回 410 Gone,不再洩漏任何資料 ===
    @app.get("/api/v1/users/<int:user_id>")
    def get_user_v1(user_id):
        return jsonify({"error": "API v1 已停止服務,請改用 v2"}), 410

    return app


if __name__ == "__main__":
    create_app().run(port=5092)
