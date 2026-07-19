"""API10:2023 不安全地取用 API — 修補後的版本。

修補方式:把第三方回來的資料當成與使用者輸入同等風險——使用前先驗證型別與
範圍(折扣必須是 0–100 的數值)。不合理就拒用(視為無折扣),不讓被污染的資料
流進金額計算。對應技能筆記的防禦對策:「將第三方資料視為與使用者輸入同等風險,
使用前務必驗證與淨化」。(正式版還應確保與第三方走加密通道、評估供應商安全狀態、
不盲從其重導向。)
"""

import requests
from flask import Flask, jsonify, request

from consumption_common import (
    MAX_DISCOUNT_PERCENT,
    MIN_DISCOUNT_PERCENT,
    THIRD_PARTY_COUPON_URL,
)

UPSTREAM_TIMEOUT_SECONDS = 3


def sanitize_discount(raw):
    """把第三方回來的折扣驗證成合理值;不合理就回 0(視為無折扣)。"""
    if not isinstance(raw, (int, float)) or isinstance(raw, bool):
        return 0
    if raw < MIN_DISCOUNT_PERCENT or raw > MAX_DISCOUNT_PERCENT:
        return 0
    return raw


def create_app():
    app = Flask(__name__)

    @app.post("/api/checkout")
    def checkout():
        base_price = (request.get_json(silent=True) or {}).get("base_price", 0)

        resp = requests.get(THIRD_PARTY_COUPON_URL, timeout=UPSTREAM_TIMEOUT_SECONDS)
        raw_discount = resp.json().get("discount_percent")

        # === 修補:驗證第三方資料,不合理就拒用 ===
        discount_percent = sanitize_discount(raw_discount)
        rejected = discount_percent != raw_discount

        final_price = base_price * (1 - discount_percent / 100)
        return jsonify({
            "base_price": base_price,
            "discount_percent": discount_percent,
            "final_price": final_price,
            "upstream_value_rejected": rejected,
        }), 200

    return app


if __name__ == "__main__":
    create_app().run(port=5102)
