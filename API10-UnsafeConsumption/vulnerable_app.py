"""API10:2023 不安全地取用 API — 有漏洞的版本。

漏洞點:結帳時去取用第三方折扣服務,拿到 discount_percent 後**未經任何驗證**
就直接套進金額計算。第三方一旦被攻擊者控制,回一個荒謬折扣,最終金額就被算成
負數(等於店家倒貼)。對應技能筆記的「過度信任第三方 API 提供的數據,未像處理
使用者輸入那樣驗證與過濾」。
"""

import requests
from flask import Flask, jsonify, request

from consumption_common import THIRD_PARTY_COUPON_URL

UPSTREAM_TIMEOUT_SECONDS = 3


def create_app():
    app = Flask(__name__)

    @app.post("/api/checkout")
    def checkout():
        base_price = (request.get_json(silent=True) or {}).get("base_price", 0)

        # 向第三方折扣服務取得折扣。
        resp = requests.get(THIRD_PARTY_COUPON_URL, timeout=UPSTREAM_TIMEOUT_SECONDS)
        discount_percent = resp.json()["discount_percent"]

        # === 漏洞:未驗證第三方資料就直接使用 ===
        final_price = base_price * (1 - discount_percent / 100)
        return jsonify({
            "base_price": base_price,
            "discount_percent": discount_percent,
            "final_price": final_price,
        }), 200

    return app


if __name__ == "__main__":
    create_app().run(port=5101)
