"""API6:2023 敏感業務流程存取不受限 — 有漏洞的版本。

漏洞點:購買端點只檢查「有沒有登入」與「還有沒有庫存」,對「同一個帳號 / 機器人
在極短時間狂刷購買」毫無防備。黃牛用一支腳本迴圈呼叫,就能一人把限量庫存整批
掃空。對應技能筆記的「PS5 搶購機器人」案例。
"""

from flask import Flask, jsonify, request

from inventory_db import ITEM_NAME, resolve_token, seed_stock


def create_app():
    app = Flask(__name__)
    stock = seed_stock()

    @app.post("/api/purchase")
    def purchase():
        buyer = resolve_token(request.headers.get("Authorization"))
        if buyer is None:
            return jsonify({"error": "unauthenticated"}), 401

        # === 漏洞:沒有每人限購、沒有速率限制、沒有真人檢測 ===
        if stock[ITEM_NAME] <= 0:
            return jsonify({"error": "sold out"}), 409
        stock[ITEM_NAME] -= 1
        return jsonify({"message": f"{buyer} 購得 1 台 {ITEM_NAME}", "remaining": stock[ITEM_NAME]}), 200

    return app


if __name__ == "__main__":
    create_app().run(port=5061)
