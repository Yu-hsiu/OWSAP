"""API6:2023 敏感業務流程存取不受限 — 修補後的版本。

修補方式:對業務流程本身加保護——每個帳號限購上限(MAX_PER_USER),超過就擋。
對應技能筆記的防禦對策:「業務層識別可能被濫用的流程,工程層選保護機制」。
(真實世界還會疊上裝置指紋、CAPTCHA / 真人檢測、分析非人類操作模式、封鎖已知
代理 / Tor 出口節點等多層防線;此處以最直接的每人限購示範核心觀念。)
"""

from flask import Flask, jsonify, request

from inventory_db import ITEM_NAME, resolve_token, seed_stock

MAX_PER_USER = 1  # 每個帳號最多可購買數量


def create_app():
    app = Flask(__name__)
    stock = seed_stock()
    purchased_by = {}  # 買家名稱 -> 已購買數量

    @app.post("/api/purchase")
    def purchase():
        buyer = resolve_token(request.headers.get("Authorization"))
        if buyer is None:
            return jsonify({"error": "unauthenticated"}), 401

        # === 修補:每人限購,阻斷單一帳號 / 機器人掃貨 ===
        if purchased_by.get(buyer, 0) >= MAX_PER_USER:
            return jsonify({"error": f"每人限購 {MAX_PER_USER} 台"}), 429
        if stock[ITEM_NAME] <= 0:
            return jsonify({"error": "sold out"}), 409

        stock[ITEM_NAME] -= 1
        purchased_by[buyer] = purchased_by.get(buyer, 0) + 1
        return jsonify({"message": f"{buyer} 購得 1 台 {ITEM_NAME}", "remaining": stock[ITEM_NAME]}), 200

    return app


if __name__ == "__main__":
    create_app().run(port=5062)
